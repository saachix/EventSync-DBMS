import tkinter as tk
from gui.sessions_screen import SessionsScreen
import tkinter.messagebox as mb

# Mock messagebox completely so script doesn't hang
mb.askyesno = lambda *args: True
mb.showinfo = lambda *args: None
mb.showerror = lambda *args: None

def run_tests():
    root = tk.Tk()
    screen = SessionsScreen(root)
    
    # 1. Existing sessions
    screen.load_data()
    children = screen.tree.get_children()
    print(f"Test 1 - Initial Sessions Count: {len(children)}")
    
    # 2. Add Valid Session
    print("Test 2 - Adding temporary session...")
    screen.var_title.set("Temp Test Session")
    screen.var_event.set("AI Innovation Workshop")
    screen.var_venue.set("Seminar Hall 1") # Capacity is 150
    screen.var_date.set("2026-11-20")
    screen.var_start.set("09:00:00")
    screen.var_end.set("10:00:00")
    screen.var_attendance.set("50")
    screen.add_session()
    
    screen.load_data()
    children_after_add = screen.tree.get_children()
    print(f"Count after add: {len(children_after_add)}")
    
    temp_id = None
    for child in children_after_add:
        values = screen.tree.item(child, 'values')
        if values[1] == "Temp Test Session":
            temp_id = values[0]
            screen.tree.selection_set(child)
            screen.tree.focus(child)
            screen.get_cursor(None)
            break
            
    # 3. Invalid Time
    print("Test 3 - Invalid time test...")
    screen.var_id.set("")
    screen.var_start.set("14:00")
    screen.var_end.set("13:00")
    if not screen.validate_and_check_overlap(): print("Rejected invalid time correctly.")
    
    # 4. Venue Capacity
    print("Test 4 - Capacity test...")
    screen.var_start.set("10:00")
    screen.var_end.set("11:00")
    screen.var_attendance.set("200") # Exceeds 150
    if not screen.validate_and_check_overlap(): print("Rejected capacity properly.")
    
    # 5. Overlap Test
    print("Test 5 - Overlap test...")
    # There is an existing session in the sample data:
    # 1, 3 (Innovation Lab), '2026-11-10', '10:00:00', '11:30:00'
    screen.var_title.set("Overlap Session")
    screen.var_venue.set("Innovation Lab")
    screen.var_date.set("2026-11-10")
    screen.var_start.set("11:00:00")
    screen.var_end.set("12:00:00")
    screen.var_attendance.set("50")
    if not screen.validate_and_check_overlap(): print("Rejected overlap properly.")
    
    # 6. Back to Back
    print("Test 6 - Back to Back test...")
    screen.var_start.set("11:30:00")
    screen.var_end.set("12:30:00")
    if screen.validate_and_check_overlap(): print("Allowed back to back properly.")
    
    # 7. Different venue overlap
    print("Test 7 - Different Venue Overlap test...")
    screen.var_venue.set("Seminar Hall 1")
    screen.var_start.set("10:00:00")
    screen.var_end.set("11:30:00")
    if screen.validate_and_check_overlap(): print("Allowed different venue properly.")
    
    # 8. Edit overlap
    print("Test 8 - Edit overlap (exclude self) test...")
    screen.var_id.set(temp_id)
    screen.var_venue.set("Seminar Hall 1")
    screen.var_date.set("2026-11-20")
    screen.var_start.set("09:00:00")
    screen.var_end.set("10:00:00")
    # This shouldn't conflict with itself
    if screen.validate_and_check_overlap(temp_id): print("Allowed editing self properly without conflict.")
    
    # 9. Delete Session
    print("Test 9 - Deleting temporary session...")
    screen.var_id.set(temp_id)
    screen.delete_session()
    
    screen.load_data()
    final_children = screen.tree.get_children()
    print(f"Final Count: {len(final_children)}")
    
    print("All backend tests completed.")

if __name__ == "__main__":
    run_tests()
