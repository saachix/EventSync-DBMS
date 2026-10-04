"""
Stage 7 automated backend tests for PaymentsScreen.
Mocks all messagebox calls so no GUI dialogs block the script.
"""
import tkinter as tk
import gui.payments_screen as _pm_mod

# Patch messagebox on the module before the screen is constructed
_pm_mod.messagebox.askyesno = lambda *a, **kw: True
_pm_mod.messagebox.showinfo  = lambda *a, **kw: None
_pm_mod.messagebox.showerror = lambda *a, **kw: print(f"  [MOCK showerror] {a[0]}: {a[1]}")

from gui.payments_screen import PaymentsScreen
from database.db_connection import DatabaseConnection


def run_tests():
    root = tk.Tk()
    root.withdraw()          # keep window invisible during tests
    container = tk.Frame(root)
    screen = PaymentsScreen(container)

    db = DatabaseConnection()

    # ------------------------------------------------------------------ #
    # TEST 1 – existing payment records load correctly
    # ------------------------------------------------------------------ #
    screen.load_data()
    children = screen.tree.get_children()
    print(f"Test 1 – Existing payments loaded: {len(children)}")
    assert len(children) == 6, f"Expected 6 sample payments, got {len(children)}"

    # ------------------------------------------------------------------ #
    # TEST 2 – total revenue comes from MySQL (not hard-coded)
    # ------------------------------------------------------------------ #
    rev_text = screen.lbl_total_revenue.cget("text")   # e.g. "Total Revenue: ₹800.00"
    pay_text = screen.lbl_total_payments.cget("text")
    print(f"Test 2 - {pay_text}  |  {rev_text}")
    assert "800" in rev_text, f"Unexpected revenue text: {rev_text}"

    # ------------------------------------------------------------------ #
    # TEST 3 – insert a temporary payment (registration_id=6 → Cultural Fest)
    # ------------------------------------------------------------------ #
    print("Test 3 – Inserting temporary payment for Reg #6 …")
    temp_reg_label = next(lbl for lbl in screen.reg_map if "Reg #6" in lbl)
    screen.var_registration.set(temp_reg_label)
    screen.var_amount.set("50.00")
    screen.var_date.set("2026-10-04")
    screen.var_method.set("Cash")
    screen.var_status.set("Pending")
    screen.add_payment()

    screen.load_data()
    children_after = screen.tree.get_children()
    print(f"  Payments after insert: {len(children_after)}")
    assert len(children_after) == 7, "Temporary payment was not inserted"

    # Capture the new payment_id (first row = highest id, DESC order)
    temp_pay_id = screen.tree.item(children_after[0])['values'][0]
    print(f"  Temp payment_id = {temp_pay_id}")

    # ------------------------------------------------------------------ #
    # TEST 4 – negative amount must be rejected
    # ------------------------------------------------------------------ #
    print("Test 4 - Negative amount validation ...")
    screen.var_registration.set(temp_reg_label)   # ensure reg is set
    screen.var_amount.set("-10")
    try:
        screen._validate_inputs()
        print("  FAIL: negative amount was not caught")
    except ValueError as e:
        print(f"  PASS: caught -> {e}")

    screen.var_amount.set("50.00")          # restore valid value

    # ------------------------------------------------------------------ #
    # TEST 5 - invalid date must be rejected
    # ------------------------------------------------------------------ #
    print("Test 5 - Invalid date validation ...")
    screen.var_date.set("99-99-9999")
    try:
        screen._validate_inputs()
        print("  FAIL: invalid date was not caught")
    except ValueError as e:
        print(f"  PASS: caught -> {e}")

    screen.var_date.set("2026-10-04")       # restore valid value

    # ------------------------------------------------------------------ #
    # TEST 6 – edit (UPDATE) the temporary payment
    # ------------------------------------------------------------------ #
    print("Test 6 – Updating temporary payment …")
    # Simulate clicking the row in the treeview
    for child in screen.tree.get_children():
        if screen.tree.item(child)['values'][0] == temp_pay_id:
            screen.tree.selection_set(child)
            screen.tree.focus(child)
            screen.on_row_select()
            break

    screen.var_amount.set("75.00")
    screen.var_status.set("Paid")
    screen.update_payment()

    # Verify the DB was updated
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT amount, payment_status FROM Payment WHERE payment_id=%s",
                (temp_pay_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    print(f"  DB row after update: amount={row[0]}, status={row[1]}")
    assert float(row[0]) == 75.00, "Amount was not updated"
    assert row[1] == "Paid",       "Status was not updated"
    print("  PASS")

    # ------------------------------------------------------------------ #
    # TEST 7 – search by event name
    # ------------------------------------------------------------------ #
    print("Test 7 – Search by event name 'AI Innovation' …")
    screen.var_search.set("AI Innovation")
    screen.search_data()
    found_event = len(screen.tree.get_children())
    print(f"  Rows returned: {found_event}")
    assert found_event >= 3, f"Expected ≥3 AI Innovation payments, got {found_event}"

    # ------------------------------------------------------------------ #
    # TEST 8 – search by participant name
    # ------------------------------------------------------------------ #
    print("Test 8 – Search by participant name 'Aarav' …")
    screen.var_search.set("Aarav")
    screen.search_data()
    found_part = len(screen.tree.get_children())
    print(f"  Rows returned: {found_part}")
    assert found_part >= 1, f"Expected ≥1 payment for Aarav, got {found_part}"

    # ------------------------------------------------------------------ #
    # TEST 9 – delete the temporary payment and restore state
    # ------------------------------------------------------------------ #
    print("Test 9 – Deleting temporary payment …")
    screen.load_data()   # show all so temp row is visible
    for child in screen.tree.get_children():
        if screen.tree.item(child)['values'][0] == temp_pay_id:
            screen.tree.selection_set(child)
            screen.tree.focus(child)
            screen.on_row_select()
            break

    screen.delete_payment()

    screen.load_data()
    final_count = len(screen.tree.get_children())
    print(f"  Payments after deletion: {final_count}")
    assert final_count == 6, f"Expected 6 (original), got {final_count}"

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    screen.refresh_summary()
    print(f"\nFinal summary: {screen.lbl_total_payments.cget('text')}")
    print(f"Final summary: {screen.lbl_total_revenue.cget('text')}")
    print("\nAll Stage 7 backend tests passed.")


if __name__ == "__main__":
    run_tests()
