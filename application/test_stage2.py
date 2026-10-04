import tkinter as tk
from gui.events_screen import EventsScreen

def run_tests():
    root = tk.Tk()
    events_screen = EventsScreen(root)
    
    # 1. Verify 3 events exist
    events_screen.load_data()
    children = events_screen.tree.get_children()
    print(f"Test 1 - Initial Events Count: {len(children)}")
    
    # 2. Add event
    events_screen.var_name.set("Temp Event")
    events_screen.var_category.set("Workshop")
    events_screen.var_coordinator.set("Priya Nair")
    events_screen.var_date.set("2026-12-31")
    events_screen.var_capacity.set("50")
    events_screen.var_fee.set("100")
    events_screen.var_status.set("Open")
    events_screen.text_desc.insert("1.0", "Temporary Description")
    
    print("Test 2 - Adding temporary event...")
    events_screen.add_event()
    
    # Reload and check count
    events_screen.load_data()
    children_after_add = events_screen.tree.get_children()
    print(f"Test 3 - Events after add: {len(children_after_add)}")
    
    # Get ID of the new event
    temp_event_id = None
    for child in children_after_add:
        values = events_screen.tree.item(child, 'values')
        if values[1] == "Temp Event":
            temp_event_id = values[0]
            # Select it in Treeview to test cursor
            events_screen.tree.selection_set(child)
            events_screen.tree.focus(child)
            events_screen.get_cursor(None)
            break
            
    print(f"Test 4 - Temp event ID: {temp_event_id}")
    
    # 3. Edit Event
    print("Test 5 - Updating temporary event...")
    events_screen.var_name.set("Updated Temp Event")
    events_screen.update_event()
    
    events_screen.load_data()
    for child in events_screen.tree.get_children():
        values = events_screen.tree.item(child, 'values')
        if values[0] == temp_event_id:
            print(f"Test 6 - Updated Name verified: {values[1]}")
            events_screen.tree.selection_set(child)
            events_screen.tree.focus(child)
            events_screen.get_cursor(None)
            break
            
    # 4. Search Event
    print("Test 7 - Searching for 'Updated Temp'...")
    events_screen.var_search.set("Updated Temp")
    events_screen.search_data()
    search_children = events_screen.tree.get_children()
    print(f"Test 8 - Search results count: {len(search_children)}")
    
    # 5. Delete Event
    print("Test 9 - Deleting temporary event...")
    # Mock messagebox to return True
    import tkinter.messagebox as mb
    mb.askyesno = lambda *args: True
    mb.showinfo = lambda *args: None
    mb.showerror = lambda *args: None
    
    events_screen.delete_event()
    
    events_screen.load_data()
    final_children = events_screen.tree.get_children()
    print(f"Test 10 - Final events count: {len(final_children)}")
    
    # 6. Invalid capacity / Negative fee test
    print("Test 11 - Testing invalid validation...")
    events_screen.var_name.set("Invalid Event")
    events_screen.var_category.set("Workshop")
    events_screen.var_coordinator.set("Priya Nair")
    events_screen.var_date.set("2026-12-31")
    
    # Negative capacity
    events_screen.var_capacity.set("-5")
    events_screen.var_fee.set("100")
    if not events_screen.validate_inputs(): print("Capacity validation works.")
    
    # Negative fee
    events_screen.var_capacity.set("50")
    events_screen.var_fee.set("-100")
    if not events_screen.validate_inputs(): print("Fee validation works.")

    # Invalid Date
    events_screen.var_fee.set("100")
    events_screen.var_date.set("2026/12/31")
    if not events_screen.validate_inputs(): print("Date validation works.")
    
    print("All backend tests completed.")

if __name__ == "__main__":
    run_tests()
