import tkinter as tk
from gui.attendance_screen import AttendanceScreen
from database.db_connection import DatabaseConnection
import tkinter.messagebox as mb

import gui.attendance_screen
gui.attendance_screen.messagebox.askyesno = lambda *args: True
gui.attendance_screen.messagebox.showinfo = lambda *args: None
gui.attendance_screen.messagebox.showerror = lambda *args: print(f"Mock Error: {args}")

def run_tests():
    root = tk.Tk()
    screen = AttendanceScreen(root)
    
    # 1. Existing attendance
    screen.load_all_attendance()
    children = screen.att_tree.get_children()
    print(f"Test 1 - Initial Attendance Count: {len(children)}")
    
    # 2. Event filtering
    print("Test 2 - Event filtering (AI Innovation Workshop)...")
    screen.var_event.set("AI Innovation Workshop")
    screen.on_event_selected()
    sessions = screen.combo_session['values']
    print(f"Available sessions for event: {len(sessions)}")
    
    if len(sessions) > 0:
        # 3. Session filtering
        print("Test 3 - Session filtering...")
        screen.var_session.set(sessions[0]) # Intro to AI
        screen.on_session_selected()
        roster_children = screen.roster_tree.get_children()
        print(f"Participants in roster for this session: {len(roster_children)}")
        
        # 4 & 5. New/Duplicate Attendance (Update to Absent)
        print("Test 4/5/6 - Update Attendance Status...")
        if roster_children:
            # Let's change the first participant's status to Absent
            screen.roster_tree.selection_set(roster_children[0])
            screen.roster_tree.focus(roster_children[0])
            
            vals = screen.roster_tree.item(roster_children[0])['values']
            old_status = vals[2]
            print(f"Old status: {old_status}")
            
            screen.mark_attendance("Absent")
            
            # Check new status
            new_vals = screen.roster_tree.item(roster_children[0])['values']
            print(f"New status: {new_vals[2]}")
            
            # Revert back to Present
            print("Test 8 - Check-in time logic (Present)...")
            screen.mark_attendance("Present")
            new_vals = screen.roster_tree.item(roster_children[0])['values']
            print(f"Reverted status: {new_vals[2]}, Time: {new_vals[3]}")
    
    # Create arbitrary new record for deletion test
    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()
    # Find a registration that has no attendance for this session
    # We will just insert an attendance directly, then delete it via GUI
    try:
        cursor.execute("INSERT INTO Attendance (registration_id, session_id, attendance_status, check_in_time) VALUES (6, 4, 'Present', '18:00:00')")
        conn.commit()
    except:
        pass # If it already exists it's fine
    
    screen.load_all_attendance()
    att_children = screen.att_tree.get_children()
    print(f"Count before delete: {len(att_children)}")
    
    # 9. Delete Attendance
    print("Test 9 - Restore test data (Delete)...")
    for child in att_children:
        vals = screen.att_tree.item(child)['values']
        if vals[1] == "Cultural Fest 2026": # Registration 6 is for Cultural Fest
            screen.att_tree.selection_set(child)
            screen.att_tree.focus(child)
            screen.delete_attendance()
            break
            
    screen.load_all_attendance()
    print(f"Final Count: {len(screen.att_tree.get_children())}")

    print("All backend tests completed.")

if __name__ == "__main__":
    run_tests()
