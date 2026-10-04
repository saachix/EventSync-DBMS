"""
Stage 8 automated backend tests for CertificatesScreen.
All messagebox calls are patched before construction so no dialogs block.
"""
import tkinter as tk
import gui.certificates_screen as _cm

_cm.messagebox.askyesno = lambda *a, **kw: True
_cm.messagebox.showinfo  = lambda *a, **kw: print(f"  [INFO] {a[1]}")
_cm.messagebox.showerror = lambda *a, **kw: print(f"  [ERROR] {a[0]}: {a[1]}")

from gui.certificates_screen import CertificatesScreen, ELIGIBLE_THRESHOLD
from database.db_connection import DatabaseConnection


PASS = "PASS"
FAIL = "FAIL"

def check(condition, msg):
    status = PASS if condition else FAIL
    print(f"  {status}: {msg}")
    return condition


def select_reg(screen, reg_id):
    """Select a registration by ID via the dropdown map."""
    label = next((l for l, rid in screen.reg_map.items() if rid == reg_id), None)
    if label is None:
        print(f"  [ERROR] reg_id {reg_id} not found in map")
        return False
    screen.var_reg.set(label)
    screen.current_reg_id = reg_id
    screen._refresh_info_panel(reg_id)
    return True


def run_tests():
    root = tk.Tk()
    root.withdraw()
    container = tk.Frame(root)
    screen = CertificatesScreen(container)

    db = DatabaseConnection()

    # ------------------------------------------------------------------ #
    # TEST 1 -- existing certificates load correctly
    # ------------------------------------------------------------------ #
    screen.load_certificates()
    rows = screen.tree.get_children()
    print(f"Test 1 - Existing certificates loaded: {len(rows)}")
    check(len(rows) == 2, f"Expected 2 sample certificates, got {len(rows)}")

    # ------------------------------------------------------------------ #
    # TEST 2 -- 100% attendance (Reg 1: Aarav, Event 1, 2/2 Present)
    # ------------------------------------------------------------------ #
    print("Test 2 - 100% case (Reg 1: Aarav, AI Innovation, 2/2 Present)...")
    select_reg(screen, 1)
    info = screen.get_attendance_info(1)
    pname, ename, total, attended, pct, cert_row = info
    check(total == 2, f"Total sessions = {total}")
    check(attended == 2, f"Sessions attended = {attended}")
    check(abs(pct - 100.0) < 0.01, f"Attendance pct = {pct:.1f}%")
    check(pct >= ELIGIBLE_THRESHOLD, f"Is eligible (>= {ELIGIBLE_THRESHOLD}%)")

    # ------------------------------------------------------------------ #
    # TEST 3 -- 50% attendance (Reg 2: Meera, Event 1, 1 Present 1 Absent)
    # ------------------------------------------------------------------ #
    print("Test 3 - 50% case (Reg 2: Meera, AI Innovation, 1/2 Present)...")
    select_reg(screen, 2)
    info = screen.get_attendance_info(2)
    pname, ename, total, attended, pct, cert_row = info
    check(total == 2, f"Total sessions = {total}")
    check(attended == 1, f"Sessions attended = {attended}")
    check(abs(pct - 50.0) < 0.01, f"Attendance pct = {pct:.1f}%")
    check(pct < ELIGIBLE_THRESHOLD, f"Is NOT eligible (< {ELIGIBLE_THRESHOLD}%)")

    # ------------------------------------------------------------------ #
    # TEST 4 -- 75% boundary (insert temporary attendance for Reg 5 to get 3/4)
    # -- Reg 5: Ishita Rao, Future Tech Seminar (1 session only)
    # -- We simulate 75% by temporarily adding extra sessions to Event 2
    # -- and controlling attendance. Easier: use a fresh temp reg.
    # ------------------------------------------------------------------ #
    print("Test 4 - 75% boundary: create temp scenario via direct DB manipulation...")
    conn = db.get_connection()
    cur = conn.cursor()

    # Add 3 temporary sessions to Event 2 (so it has 4 total)
    cur.execute("INSERT INTO Venue (venue_name, location, capacity) VALUES ('Temp Venue', 'Test', 50)")
    conn.commit()
    tmp_venue_id = cur.lastrowid

    tmp_session_ids = []
    for i in range(3):
        cur.execute("""INSERT INTO Session (event_id, venue_id, session_title, session_date,
                       start_time, end_time, expected_attendance)
                       VALUES (2, %s, %s, '2026-12-01', %s, %s, 10)""",
                    (tmp_venue_id, f"Temp Session {i+1}",
                     f"{10+i}:00:00", f"{11+i}:00:00"))
        conn.commit()
        tmp_session_ids.append(cur.lastrowid)

    # Event 2 now has 4 sessions (original 1 + 3 temp)
    # Reg 4: Aarav, Future Tech Seminar -- already has 1 Present for session 3
    # Add Present for 2 of the 3 temp sessions → 3/4 = 75%
    for sid in tmp_session_ids[:2]:
        cur.execute("""INSERT INTO Attendance (registration_id, session_id,
                       attendance_status, check_in_time) VALUES (4, %s, 'Present', '09:00:00')""",
                    (sid,))
    conn.commit()

    # Refresh screen dropdown
    screen.load_registrations()
    info4 = screen.get_attendance_info(4)
    pname4, ename4, total4, attended4, pct4, cert4 = info4
    print(f"  Reg 4: total={total4}, attended={attended4}, pct={pct4:.1f}%")
    check(total4 == 4, f"Total sessions = {total4} (expected 4)")
    check(attended4 == 3, f"Sessions attended = {attended4} (expected 3)")
    check(abs(pct4 - 75.0) < 0.01, f"Attendance pct = {pct4:.1f}% (expected 75.0%)")
    check(pct4 >= ELIGIBLE_THRESHOLD,
          f"75% is ELIGIBLE (>= {ELIGIBLE_THRESHOLD}%)")

    # Cleanup temp sessions and attendance (venue stays for now)
    cur.execute("DELETE FROM Attendance WHERE session_id IN (%s,%s,%s)",
                tuple(tmp_session_ids))
    cur.execute("DELETE FROM Session WHERE session_id IN (%s,%s,%s)",
                tuple(tmp_session_ids))
    cur.execute("DELETE FROM Venue WHERE venue_id = %s", (tmp_venue_id,))
    conn.commit()

    # ------------------------------------------------------------------ #
    # TEST 5 -- missing attendance records count as Not Attended
    # ------------------------------------------------------------------ #
    print("Test 5 - Missing attendance records count as absent...")
    # Reg 6: Kabir Joshi, Cultural Fest (1 session). No attendance record inserted.
    info6 = screen.get_attendance_info(6)
    p6, e6, total6, att6, pct6, cert6 = info6
    print(f"  Reg 6: total={total6}, attended={att6}, pct={pct6:.1f}%")
    check(total6 == 1, f"Cultural Fest has 1 session (got {total6})")
    check(att6 == 0, f"No attendance record = 0 attended (got {att6})")
    check(pct6 < ELIGIBLE_THRESHOLD, "Not eligible without attendance records")

    # ------------------------------------------------------------------ #
    # TEST 6 -- generate certificate for an eligible registration with none yet
    # Reg 4: Aarav / Future Tech Seminar -- 1/1 = 100%, no cert yet
    # ------------------------------------------------------------------ #
    print("Test 6 - Generate certificate for eligible Reg 4...")
    select_reg(screen, 4)
    screen.generate_certificate()   # should succeed
    screen.load_certificates()
    rows_after = screen.tree.get_children()
    print(f"  Certificates after generate: {len(rows_after)}")
    check(len(rows_after) == 3, f"Expected 3 certs (was 2 + new), got {len(rows_after)}")

    # Capture new cert id for cleanup
    info4b = screen.get_attendance_info(4)
    new_cert_row = info4b[5]
    new_cert_id = new_cert_row[0] if new_cert_row else None
    print(f"  New certificate_id = {new_cert_id}")

    # ------------------------------------------------------------------ #
    # TEST 7 -- ineligible participant blocked
    # Reg 2: Meera 50% -- no cert should be inserted
    # ------------------------------------------------------------------ #
    print("Test 7 - Block certificate for ineligible Reg 2 (Meera, 50%)...")
    select_reg(screen, 2)
    screen.generate_certificate()   # should be blocked
    cur.execute("SELECT certificate_id FROM Certificate WHERE registration_id=2")
    row = cur.fetchone()
    check(row is None, "No certificate inserted for ineligible participant")

    # ------------------------------------------------------------------ #
    # TEST 8 -- duplicate certificate blocked
    # Reg 1: already has a certificate (from sample data)
    # ------------------------------------------------------------------ #
    print("Test 8 - Block duplicate certificate for Reg 1 (Aarav, already issued)...")
    select_reg(screen, 1)
    screen.generate_certificate()   # should be blocked
    cur.execute("SELECT COUNT(*) FROM Certificate WHERE registration_id=1")
    dup_count = cur.fetchone()[0]
    check(dup_count == 1, f"Still only 1 certificate for Reg 1 (got {dup_count})")

    # ------------------------------------------------------------------ #
    # TEST 9 -- search
    # ------------------------------------------------------------------ #
    print("Test 9 - Search by participant name 'Aarav'...")
    screen.load_certificates()
    screen.var_search.set("Aarav")
    screen.search_certificates()
    aarav_rows = screen.tree.get_children()
    print(f"  Search results: {len(aarav_rows)}")
    check(len(aarav_rows) >= 1, "At least 1 cert found for Aarav")

    print("Test 9b - Search by event name 'AI Innovation'...")
    screen.var_search.set("AI Innovation")
    screen.search_certificates()
    ai_rows = screen.tree.get_children()
    print(f"  Search results: {len(ai_rows)}")
    check(len(ai_rows) >= 2, "At least 2 certs found for AI Innovation")

    # ------------------------------------------------------------------ #
    # TEST 10 -- cleanup: delete temp certificate for Reg 4
    # ------------------------------------------------------------------ #
    print("Test 10 - Cleanup: deleting temp certificate for Reg 4...")
    if new_cert_id:
        cur.execute("DELETE FROM Certificate WHERE certificate_id = %s",
                    (new_cert_id,))
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM Certificate")
    final_count = cur.fetchone()[0]
    print(f"  Final certificate count: {final_count}")
    check(final_count == 2, f"Restored to original 2 certificates (got {final_count})")

    cur.close()
    conn.close()

    screen.load_certificates()
    print(f"\nAll Stage 8 backend tests completed.")


if __name__ == "__main__":
    run_tests()
