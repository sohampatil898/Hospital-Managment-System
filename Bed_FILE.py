from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
import sqlite3
import os

# NOTE: Removed top-level import to prevent circular import errors
# import page_after_login

def open_beds(window):
    
    for widget in window.winfo_children():
        widget.destroy()
        
    window.title("Bed Management System")
    window.state('zoomed')
    window.configure(bg="#F1F5F9")
    
    # --- DATABASE CONNECTION ---
    def get_db_connection():
        if os.path.exists('Hospital.db'): return sqlite3.connect('Hospital.db')
        elif os.path.exists('hospital.db'): return sqlite3.connect('hospital.db')
        else: return sqlite3.connect('database1.db')

    connector = get_db_connection()
    
    # Create Table
    connector.execute("""CREATE TABLE IF NOT EXISTS BED_MANAGEMENT (
        BED_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        PATIENT_NAME TEXT,
        WARD TEXT, 
        BED_NO TEXT, 
        STATUS TEXT,
        PRICE_PER_DAY TEXT
    )""")

    # --- DATABASE AUTO-FIXER (Ensures columns exist) ---
    try: connector.execute("ALTER TABLE BED_MANAGEMENT ADD COLUMN PRICE_PER_DAY TEXT")
    except: pass 
    try: connector.execute("ALTER TABLE BED_MANAGEMENT ADD COLUMN PATIENT_NAME TEXT")
    except: pass

    def display_records():
        tree.delete(*tree.get_children())
        curr = connector.execute('SELECT BED_ID, PATIENT_NAME, WARD, BED_NO, STATUS, PRICE_PER_DAY FROM BED_MANAGEMENT')
        data = curr.fetchall()
        for records in data:
            tree.insert('', END, values=records)

    def add_bed():
        p_name = name_var.get()
        ward = ward_var.get()
        bed_no = bed_var.get()
        status = status_var.get()
        price = price_var.get()

        if not p_name or not bed_no or not price:
            mb.showerror("Error", "Please fill all details!")
            return

        try:
            connector.execute(
                'INSERT INTO BED_MANAGEMENT (PATIENT_NAME, WARD, BED_NO, STATUS, PRICE_PER_DAY) VALUES (?,?,?,?,?)', 
                (p_name, ward, bed_no, status, price)
            )
            connector.commit()
            mb.showinfo('Success', 'Bed Allocated Successfully')
            clear_fields()
            display_records()
        except Exception as e:
            mb.showerror('Error', str(e))

    def discharge_bed():
        if not tree.selection():
            mb.showerror('Error', 'Please select a bed to discharge')
            return
        
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values["values"]
        bed_id = selection[0]

        connector.execute('DELETE FROM BED_MANAGEMENT WHERE BED_ID=?', (bed_id,))
        connector.commit()
        mb.showinfo('Success', 'Patient Discharged / Bed Freed')
        display_records()

    def clear_fields():
        name_var.set("")
        bed_var.set("")
        price_var.set("")
        status_var.set("Occupied")
        ward_var.set("General Ward")

    def back():
        # Import placed inside the function to avoid circular dependency
        import page_after_login
        page_after_login.page_after_login(window)

    # --- UI LAYOUT ---
    
    # Header
    header = Frame(window, bg="#0F172A", height=70)
    header.pack(fill=X)
    Label(header, text="🛏 Bed & Ward Management", font=("Segoe UI", 20, "bold"), bg="#0F172A", fg="white").pack(side=LEFT, padx=20, pady=15)

    # Input Frame
    top_frame = Frame(window, bg="white", pady=15)
    top_frame.pack(fill=X, padx=20, pady=20)

    name_var = StringVar()
    ward_var = StringVar(value="General Ward")
    bed_var = StringVar()
    status_var = StringVar(value="Occupied")
    price_var = StringVar()

    Label(top_frame, text="Patient Name:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=LEFT, padx=(20, 5))
    Entry(top_frame, textvariable=name_var, font=("Segoe UI", 10), bg="#F8FAFC", bd=1, relief="solid", width=15).pack(side=LEFT, padx=5)

    Label(top_frame, text="Ward Type:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=LEFT, padx=(20, 5))
    
    # --- UPDATED: Added "VIP Suite" to list ---
    ward_options = ["General Ward", "Private Room", "ICU", "Recovery Ward", "VIP Suite"]
    OptionMenu(top_frame, ward_var, *ward_options).pack(side=LEFT, padx=5)

    Label(top_frame, text="Bed No:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=LEFT, padx=(20, 5))
    Entry(top_frame, textvariable=bed_var, font=("Segoe UI", 10), bg="#F8FAFC", bd=1, relief="solid", width=8).pack(side=LEFT, padx=5)

    Label(top_frame, text="Price/Day:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=LEFT, padx=(20, 5))
    Entry(top_frame, textvariable=price_var, font=("Segoe UI", 10), bg="#F8FAFC", bd=1, relief="solid", width=8).pack(side=LEFT, padx=5)

    # Buttons
    Button(top_frame, text="➕ Add Bed", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5, cursor="hand2", command=add_bed).pack(side=LEFT, padx=20)
    Button(top_frame, text="Back to Menu", bg="#EF4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5, cursor="hand2", command=back).pack(side=RIGHT, padx=20)
    Button(top_frame, text="Discharge", bg="#F59E0B", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5, cursor="hand2", command=discharge_bed).pack(side=RIGHT, padx=5)

    # Table
    tree_frame = Frame(window, bg="white", highlightbackground="#CBD5E1", highlightthickness=1)
    tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

    columns = ('ID', 'Patient', 'Ward', 'Bed No', 'Status', 'Price')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
    
    # Columns Setup
    tree.heading('ID', text='ID')
    tree.heading('Patient', text='Patient Name')
    tree.heading('Ward', text='Ward Type')
    tree.heading('Bed No', text='Bed No')
    tree.heading('Status', text='Status')
    tree.heading('Price', text='Price/Day')

    tree.column('ID', width=50)
    tree.column('Patient', width=150)
    tree.column('Ward', width=120)
    
    tree.pack(fill=BOTH, expand=True)

    display_records()

if __name__ == "__main__":
    test_window = Tk()
    open_beds(test_window)
    test_window.mainloop()