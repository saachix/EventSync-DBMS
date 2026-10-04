import tkinter as tk
from gui.participants_screen import ParticipantsScreen
import tkinter.messagebox as mb

# Mock messagebox completely so script doesn't hang
mb.askyesno = lambda *args: True
mb.showinfo = lambda *args: None
mb.showerror = lambda *args: None

def run_tests():
    root = tk.Tk()
    screen = ParticipantsScreen(root)
    
    # 1. Verify 5 participants exist
    screen.load_data()
    children = screen.tree.get_children()
    print(f"Test 1 - Initial Participants Count: {len(children)}")
    
    # 2. Add temporary participant
    screen.var_name.set("John Doe")
    screen.var_email.set("john@example.com")
    screen.var_phone.set("1234567890")
    screen.var_dept.set("Computer Science")
    screen.var_year.set("2")
    
    print("Test 2 - Adding temporary participant...")
    screen.add_participant()
    
    screen.load_data()
    children_after_add = screen.tree.get_children()
    print(f"Test 3 - Participants after add: {len(children_after_add)}")
    
    # Find new ID
    temp_id = None
    for child in children_after_add:
        values = screen.tree.item(child, 'values')
        if values[2] == "john@example.com":
            temp_id = values[0]
            screen.tree.selection_set(child)
            screen.tree.focus(child)
            screen.get_cursor(None)
            break
            
    # 3. Edit participant
    print("Test 4 - Updating temporary participant...")
    screen.var_name.set("Johnathan Doe")
    screen.update_participant()
    
    screen.load_data()
    for child in screen.tree.get_children():
        values = screen.tree.item(child, 'values')
        if values[0] == temp_id:
            print(f"Test 5 - Updated Name verified: {values[1]}")
            break
            
    # 4. Search participant
    print("Test 6 - Searching for 'Johnathan'...")
    screen.var_search.set("Johnathan")
    screen.search_data()
    search_children = screen.tree.get_children()
    print(f"Test 7 - Search results count: {len(search_children)}")
    
    # 5. Duplicate Email test
    print("Test 8 - Testing Duplicate Email Validation...")
    screen.var_id.set("") # Clear ID to add new
    screen.var_email.set("aarav@example.com") # Exists in sample_data.sql
    screen.add_participant() # Will fail and show mocked error
    
    # 6. Invalid Year test
    print("Test 9 - Testing Invalid Year Validation...")
    screen.var_email.set("john2@example.com") 
    screen.var_year.set("-1")
    if not screen.validate_inputs(): print("Year validation works.")
    
    # 7. Delete participant
    print("Test 10 - Deleting temporary participant...")
    screen.var_id.set(temp_id)
    screen.delete_participant()
    
    screen.load_data()
    final_children = screen.tree.get_children()
    print(f"Test 11 - Final participants count: {len(final_children)}")
    
    # 8. Try to delete a participant with FK dependencies (Aarav Patel from sample data)
    print("Test 12 - Testing Foreign Key Restriction...")
    for child in final_children:
        values = screen.tree.item(child, 'values')
        if values[2] == "aarav@example.com":
            screen.var_id.set(values[0])
            screen.delete_participant() # Will fail with FK restriction and show mocked error
            break
            
    print("All backend tests completed.")

if __name__ == "__main__":
    run_tests()
