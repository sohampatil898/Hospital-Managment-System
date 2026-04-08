from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import os
from tkcalendar import DateEntry 

# --- NOTE: Import moved inside functions to prevent circular import crashes ---
# import page_after_login 

def open_surgery(window):
    # 1. Clear existing widgets
    for widget in window.winfo_children():
        widget.destroy()
        
    window.geometry('1280x720')
    window.state('zoomed')
    window.title("Surgery Department & Pricing")
    window.configure(bg='#F8F9FA')

    # --- DATABASE CONNECTION ---
    def get_db_connection():
        if os.path.exists('Hospital.db'):
            return sqlite3.connect('Hospital.db')
        elif os.path.exists('hospital.db'):
            return sqlite3.connect('hospital.db')
        else:
            return sqlite3.connect('database1.db')

    # --- FUNCTIONS ---
    def auto_fill_price(event):
        """Automatically sets the price based on surgery type"""
        s_type = type_var.get().lower()
        price = 0
        
        # Pricing Logic
        if "heart" in s_type: price = 150000
        elif "knee" in s_type: price = 120000
        elif "hip" in s_type: price = 130000
        elif "brain" in s_type: price = 200000
        elif "eye" in s_type or "cataract" in s_type: price = 25000
        elif "appendix" in s_type: price = 40000
        elif "cesarean" in s_type: price = 60000
        elif "plastic" in s_type: price = 80000
        elif "hernia" in s_type: price = 45000
        else: price = 15000 # Base charge for "Other"
            
        price_var.set(price)

    def save_data():
        p_name = name_var.get()
        doc = doc_var.get()
        s_type = type_var.get()
        s_date = date_entry.get()
        s_status = status_var.get()
        s_price = price_var.get()
        
        if p_name == "" or s_type == "":
            mb.showerror("Error", "Patient Name and Surgery Type are required!")
            return

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS surgery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                doctor TEXT,
                surgery_type TEXT,
                date TEXT,
                status TEXT,
                price REAL
            )""")
            try: c.execute("ALTER TABLE surgery ADD COLUMN status TEXT")
            except: pass
            try: c.execute("ALTER TABLE surgery ADD COLUMN price REAL")
            except: pass

            c.execute("INSERT INTO surgery (patient_name, doctor, surgery_type, date, status, price) VALUES (?, ?, ?, ?, ?, ?)", 
                      (p_name, doc, s_type, s_date, s_status, s_price))
            
            conn.commit()
            conn.close()
            mb.showinfo("Success", "Surgery Scheduled Successfully!")
            clear_form()
            refresh_table()
            
        except Exception as e:
            mb.showerror("Error", f"Database Error: {e}")

    def update_data():
        try:
            selected_item = tree.selection()[0]
            val = tree.item(selected_item)['values']
            curr_id = val[0]
        except:
            mb.showerror("Error", "Please select a record to update.")
            return

        p_name = name_var.get()
        doc = doc_var.get()
        s_type = type_var.get()
        s_date = date_entry.get()
        s_status = status_var.get()
        s_price = price_var.get()

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""UPDATE surgery SET patient_name=?, doctor=?, surgery_type=?, date=?, status=?, price=? WHERE id=?""", 
                      (p_name, doc, s_type, s_date, s_status, s_price, curr_id))
            conn.commit()
            conn.close()
            mb.showinfo("Success", "Record Updated Successfully!")
            clear_form()
            refresh_table()
        except Exception as e:
            mb.showerror("Error", str(e))

    def delete_data():
        try:
            selected_item = tree.selection()[0]
            val = tree.item(selected_item)['values']
            curr_id = val[0]
        except:
            mb.showerror("Error", "Please select a record to delete.")
            return

        if mb.askyesno("Confirm", "Are you sure you want to delete this record?"):
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("DELETE FROM surgery WHERE id=?", (curr_id,))
                conn.commit()
                conn.close()
                clear_form()
                refresh_table()
            except Exception as e:
                mb.showerror("Error", str(e))

    def get_selected_row(event):
        try:
            selected_item = tree.selection()[0]
            row = tree.item(selected_item)['values']
            # Row = [ID, Name, Doctor, Type, Date, Status, Price]
            name_var.set(row[1])
            doc_var.set(row[2])
            type_var.set(row[3])
            date_entry.set_date(row[4])
            status_var.set(row[5])
            price_var.set(row[6])
        except: pass

    def clear_form():
        name_var.set("")
        doc_var.set("")
        type_var.set("")
        status_var.set("Scheduled")
        price_var.set("0")
        try: date_entry.set_date(None)
        except: pass

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT id, patient_name, doctor, surgery_type, date, status, price FROM surgery")
            rows = c.fetchall()
            for row in rows:
                safe_row = [x if x is not None else "" for x in row]
                tree.insert("", END, values=safe_row)
            conn.close()
        except Exception as e:
            print(e)

    # 2. Corrected Back Function
    def back():
        import page_after_login
        page_after_login.page_after_login(window)

    # --- GUI HEADER ---
    header = Frame(window, bg="#2C3E50", height=60)
    header.pack(fill=X)
    Label(header, text="Surgery Department", font=("Segoe UI", 18, "bold"), bg="#2C3E50", fg="white").pack(side=LEFT, padx=20, pady=10)
    
    # 3. Fixed command: 'go_back' changed to 'back'
    Button(header, text="⬅ Back to Dashboard", bg="#E74C3C", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=10,
           command=back).pack(side=RIGHT, padx=20, pady=10)

    # --- MAIN CONTENT ---
    main_frame = Frame(window, bg="#F8F9FA")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # LEFT SIDE: FORM
    form_frame = Frame(main_frame, bg="white", width=400, relief=RIDGE, bd=1)
    form_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)
    form_frame.pack_propagate(False)

    Label(form_frame, text="Schedule Surgery", font=("Segoe UI", 16, "bold"), bg="white", fg="#34495E").pack(pady=20)

    # Variables
    name_var = StringVar()
    doc_var = StringVar()
    type_var = StringVar()
    status_var = StringVar(value="Scheduled")
    price_var = StringVar(value="0")

    def create_label(text):
        Label(form_frame, text=text, font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20, pady=(15, 5))

    # 1. Patient Name
    create_label("Patient Name")
    Entry(form_frame, textvariable=name_var, font=("Segoe UI", 11), bg="#F1F2F6", bd=0, relief=FLAT).pack(fill=X, padx=20, ipady=5)

    # 2. Doctor Name
    create_label("Surgeon / Doctor")
    Entry(form_frame, textvariable=doc_var, font=("Segoe UI", 11), bg="#F1F2F6", bd=0, relief=FLAT).pack(fill=X, padx=20, ipady=5)

    # 3. Surgery Type (Dropdown with Auto-Price)
    create_label("Surgery Type")
    surgery_options = [
        "Appendectomy", "Cataract Surgery", "Cesarean Section", "Heart Bypass", 
        "Hip Replacement", "Knee Replacement", "Gallbladder Removal", 
        "Hernia Repair", "Tonsillectomy", "Plastic Surgery", "Brain surhery","S[pine surgery","Kidney Stone Removal",
        "Prostate Surgery","Pediatric Appendectomy","Congenital Repairs","Varicose Vein Surgery","Jaw Surgery",
        "Colon Resection","Tumor Removal","Kidney/Liver Transplant","Gastric Bypass","Thyroid Surgery"
    ]
    cb_type = ttk.Combobox(form_frame, textvariable=type_var, values=surgery_options, font=("Segoe UI", 11), state="readonly")
    cb_type.pack(fill=X, padx=20, ipady=5)
    cb_type.bind("<<ComboboxSelected>>", auto_fill_price) 

    # 4. Price Field (New)
    create_label("Estimated Cost ($)")
    Entry(form_frame, textvariable=price_var, font=("Segoe UI", 11), bg="#E8F5E9", bd=0, relief=FLAT).pack(fill=X, padx=20, ipady=5)

    # 5. Date
    create_label("Date")
    date_entry = DateEntry(form_frame, width=30, background='#1A73E8', foreground='white', borderwidth=2, font=("Segoe UI", 11))
    date_entry.pack(fill=X, padx=20, ipady=5)

    # 6. Status
    create_label("Status")
    status_options = ["Scheduled", "Completed", "Cancelled"]
    ttk.Combobox(form_frame, textvariable=status_var, values=status_options, font=("Segoe UI", 11), state="readonly").pack(fill=X, padx=20, ipady=5)

    # --- BUTTONS ---
    btn_frame = Frame(form_frame, bg="white")
    btn_frame.pack(fill=X, padx=20, pady=30)

    # Add Button (Full Width)
    Button(btn_frame, text="SAVE RECORD", bg="#1A73E8", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=10, cursor="hand2", command=save_data).pack(fill=X, pady=5)

    # Row for Update/Delete
    row_btns = Frame(btn_frame, bg="white")
    row_btns.pack(fill=X, pady=5)
    Button(row_btns, text="UPDATE", bg="#F39C12", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, width=15, command=update_data).pack(side=LEFT, padx=(0,5))
    Button(row_btns, text="DELETE", bg="#E74C3C", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, width=15, command=delete_data).pack(side=RIGHT, padx=(5,0))

    # Clear Button
    Button(btn_frame, text="CLEAR FORM", bg="#95A5A6", fg="white", bd=0, pady=5, command=clear_form).pack(fill=X, pady=10)

    # RIGHT SIDE: TABLE
    table_frame = Frame(main_frame, bg="white", relief=RIDGE, bd=1)
    table_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

    scroll_y = Scrollbar(table_frame, orient=VERTICAL)
    scroll_x = Scrollbar(table_frame, orient=HORIZONTAL)

    columns = ("ID", "Name", "Doctor", "Type", "Date", "Status", "Price")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                        yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    
    scroll_y.config(command=tree.yview)
    scroll_y.pack(side=RIGHT, fill=Y)
    scroll_x.config(command=tree.xview)
    scroll_x.pack(side=BOTTOM, fill=X)
    
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Patient Name")
    tree.heading("Doctor", text="Surgeon/Doctor")
    tree.heading("Type", text="Surgery Type")
    tree.heading("Date", text="Date")
    tree.heading("Status", text="Status")
    tree.heading("Price", text="Price ($)")

    tree.column("ID", width=40, anchor=CENTER)
    tree.column("Name", width=120)
    tree.column("Doctor", width=120)
    tree.column("Type", width=150)
    tree.column("Date", width=90, anchor=CENTER)
    tree.column("Status", width=90, anchor=CENTER)
    tree.column("Price", width=90, anchor=CENTER)

    tree.pack(fill=BOTH, expand=True, padx=5, pady=5)
    tree.bind('<ButtonRelease-1>', get_selected_row)
    
    refresh_table()

    # 4. REMOVED window.mainloop() (Prevents freeze)

# 5. Fixed testing block
if __name__ == "__main__":
    test_window = Tk()
    open_surgery(test_window)
    test_window.mainloop()