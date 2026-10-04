import tkinter as tk
from gui.registration_screen import RegistrationScreen
from database.db_connection import DatabaseConnection
import tkinter.messagebox as mb

# Mock messageboxes
mb.askyesno = lambda *args: True  # Auto-yes for waitlist offers and deletes
mb.showinfo = lambda *args: None
mb.showerror = lambda *args: None

def run_tests():
    root = tk.Tk()
    screen = RegistrationScreen(root)
    
    # 1. Verify initial data
    screen.load_data()
    reg_children = screen.reg_tree.get_children()
    wait_children = screen.wait_tree.get_children()
    print(f"Test 1 - Initial Registrations: {len(reg_children)}")
    print(f"Test 1 - Initial Waitlist: {len(wait_children)}")
    
    # Create temporary low-capacity event for testing
    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Event (event_name, category_id, coordinator_id, event_date, max_capacity, registration_fee, status) VALUES ('Cap Test Event', 1, 1, '2026-11-20', 1, 0, 'Open')")
    conn.commit()
    test_event_id = cursor.lastrowid
    screen.load_dropdowns() # reload event map
    
    # Get arbitrary participants
    cursor.execute("SELECT participant_name FROM Participant LIMIT 3")
    participants = [p[0] for p in cursor.fetchall()]
    p1, p2, p3 = participants[0], participants[1], participants[2]
    
    # 2. Registration Capacity Display (Existing event AI Innovation Workshop)
    print("Test 2 - Capacity Display Check...")
    screen.var_event.set("AI Innovation Workshop")
    screen.update_capacity_display()
    print(f"Cap text max: {screen.lbl_cap_max.cget('text')}")
    print(f"Cap text reg: {screen.lbl_cap_reg.cget('text')}")
    
    # 3. Valid Registration
    print("Test 3 - Valid Registration (Cap=1)...")
    screen.var_event.set("Cap Test Event")
    screen.var_participant.set(p1)
    screen.var_date.set("2026-10-04")
    screen.register_participant()
    
    screen.load_data()
    print(f"Registrations after valid reg: {len(screen.reg_tree.get_children())}")
    
    # 4. Duplicate Registration
    print("Test 4 - Duplicate Registration...")
    screen.var_event.set("Cap Test Event")
    screen.var_participant.set(p1)
    screen.register_participant() # Should catch duplicate and skip
    screen.load_data()
    print(f"Registrations after dup attempt: {len(screen.reg_tree.get_children())}")
    
    # 5. Full Event / Waitlist logic
    print("Test 5 - Full Event Waitlist Trigger...")
    screen.var_event.set("Cap Test Event")
    screen.var_participant.set(p2) # Capacity is 1, so p2 will hit capacity block and trigger askyesno -> Waitlist
    screen.var_date.set("2026-10-04")
    screen.register_participant()
    
    screen.load_data()
    new_wait = len(screen.wait_tree.get_children())
    print(f"Waitlist count after overflow: {new_wait}")
    
    # 6. Waitlist Position check
    print("Test 6 - Waitlist position sequential test...")
    screen.var_event.set("Cap Test Event")
    screen.var_participant.set(p3)
    screen.var_date.set("2026-10-04")
    screen.register_participant() # Hits capacity block, added to waitlist
    
    screen.load_data()
    for child in screen.wait_tree.get_children():
        vals = screen.wait_tree.item(child, 'values')
        if vals[1] == "Cap Test Event" and vals[2] == p3:
            print(f"P3 Waitlist Position Assigned: {vals[4]}") # Should be 2
            
    # 7. Duplicate Waitlist
    print("Test 7 - Duplicate waitlist...")
    screen.var_event.set("Cap Test Event")
    screen.var_participant.set(p2)
    screen.var_date.set("2026-10-04")
    screen.register_participant() # Should be caught by is_waitlisted check
    
    # 8. Search
    print("Test 8 - Searching...")
    screen.var_search.set("Cap Test Event")
    screen.search_data()
    print(f"Search results reg: {len(screen.reg_tree.get_children())}")
    
    # 9. Cleanup
    print("Test 9 - Deleting Temp Data...")
    cursor.execute("DELETE FROM Waitlist WHERE event_id=%s", (test_event_id,))
    cursor.execute("DELETE FROM Registration WHERE event_id=%s", (test_event_id,))
    cursor.execute("DELETE FROM Event WHERE event_id=%s", (test_event_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    screen.load_data()
    print(f"Final Registrations: {len(screen.reg_tree.get_children())}")
    print(f"Final Waitlist: {len(screen.wait_tree.get_children())}")
    
    print("All backend tests completed.")

if __name__ == "__main__":
    run_tests()
