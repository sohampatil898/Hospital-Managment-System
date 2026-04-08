from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import os

def Show_Doctor_Info(window):
    # --- WINDOW SETUP ---
    for widget in window.winfo_children():
        widget.destroy()

    window.title("Doctor Management | Hospital System")
    window.state('zoomed')
    window.configure(bg="#F1F5F9")
    
    # --- DATABASE CONNECTION ---
    def get_db():
        if os.path.exists('Hospital.db'): return sqlite3.connect('Hospital.db')
        elif os.path.exists('hospital.db'): return sqlite3.connect('hospital.db')
        else: return sqlite3.connect('database1.db')

    # Create Table if it doesn't exist
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS doctors (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT,
            CATEGORY TEXT,
            SPECIALIZATION TEXT,
            MOBILE TEXT,
            AVAILABILITY TEXT
        )""")
        conn.commit()
        conn.close()
    except Exception as e:
        mb.showerror("Database Error", f"Error setting up database: {e}")

    # --- FUNCTIONS ---
    def go_back():
        import page_after_login
        page_after_login.page_after_login(window)

    def add_doctor():
        if not name_var.get() or not mobile_var.get():
            mb.showerror("Error", "Name and Mobile are required!")
            return
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO doctors (NAME, CATEGORY, SPECIALIZATION, MOBILE, AVAILABILITY) VALUES (?,?,?,?,?)",
                           (name_var.get(), cat_var.get(), spec_var.get(), mobile_var.get(), avail_var.get()))
            conn.commit()
            conn.close()
            mb.showinfo("Success", "Doctor Added Successfully!")
            clear_form()
            display_data()
        except Exception as e:
            mb.showerror("Error", str(e))

    def update_doctor():
        try:
            selected_item = tree.selection()[0]
            cur_id = tree.item(selected_item)['values'][0]
        except:
            mb.showerror("Error", "Please select a doctor to update.")
            return

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE doctors SET NAME=?, CATEGORY=?, SPECIALIZATION=?, MOBILE=?, AVAILABILITY=? WHERE ID=?",
                           (name_var.get(), cat_var.get(), spec_var.get(), mobile_var.get(), avail_var.get(), cur_id))
            conn.commit()
            conn.close()
            mb.showinfo("Success", "Doctor Details Updated!")
            clear_form()
            display_data()
        except Exception as e:
            mb.showerror("Error", str(e))

    def delete_doctor():
        try:
            selected_item = tree.selection()[0]
            cur_id = tree.item(selected_item)['values'][0]
        except:
            mb.showerror("Error", "Please select a doctor to delete.")
            return
        
        if mb.askyesno("Confirm", "Are you sure you want to delete this doctor?"):
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM doctors WHERE ID=?", (cur_id,))
                conn.commit()
                conn.close()
                display_data()
                clear_form()
            except Exception as e:
                mb.showerror("Error", str(e))

    def clear_form():
        name_var.set("")
        cat_var.set("Consultant")
        spec_var.set("General Surgery")
        mobile_var.set("")
        avail_var.set("Available")

    def display_data():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctors")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                tree.insert("", END, values=row)
        except: pass

    def get_selected_row(event):
        try:
            selected_item = tree.selection()[0]
            row = tree.item(selected_item)['values']
            name_var.set(row[1])
            cat_var.set(row[2])
            spec_var.set(row[3])
            mobile_var.set(row[4])
            avail_var.set(row[5])
        except: pass

    # --- UI LAYOUT ---

    # Header
    header = Frame(window, bg="#0F172A", height=70)
    header.pack(fill=X)
    Label(header, text="👨‍⚕️ Doctor Management", font=("Segoe UI", 20, "bold"), bg="#0F172A", fg="white").pack(side=LEFT, padx=20, pady=15)
    Button(header, text="⬅ Back to Dashboard", bg="#DC2626", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, command=go_back).pack(side=RIGHT, padx=20, pady=15)

    # Main Content Area
    content = Frame(window, bg="#F1F5F9")
    content.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # LEFT: Entry Form
    form_frame = Frame(content, bg="white", width=400)
    form_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
    form_frame.pack_propagate(False)

    Label(form_frame, text="Doctor Details", font=("Segoe UI", 14, "bold"), bg="white", fg="#1E293B").pack(pady=20)

    # Variables
    name_var = StringVar()
    cat_var = StringVar(value="Consultant")
    spec_var = StringVar(value="General Surgery")
    mobile_var = StringVar()
    avail_var = StringVar(value="Available")

    def create_field(lbl, var, type="entry", options=None):
        Label(form_frame, text=lbl, font=("Segoe UI", 10, "bold"), bg="white", fg="#64748B", anchor="w").pack(fill=X, padx=20, pady=(10,0))
        if type == "combo":
            ttk.Combobox(form_frame, textvariable=var, values=options, state="readonly", font=("Segoe UI", 10)).pack(fill=X, padx=20, pady=5)
        else:
            Entry(form_frame, textvariable=var, font=("Segoe UI", 10), bg="#F8FAFC", relief=FLAT, highlightthickness=1, highlightbackground="#E2E8F0").pack(fill=X, padx=20, pady=5, ipady=4)

    create_field("Doctor Name", name_var)
    
    # 1. UPDATED CATEGORY LIST (Ranks/Titles)
    create_field("Category / Rank", cat_var, "combo", 
                 ["Consultant", "Senior Consultant", "Surgeon", "Resident Doctor", "Visiting Specialist", "Chief Surgeon"])
    
    # 2. EXTENSIVE SURGERY TYPES LIST
    surgery_types = [
        "General Surgery",
        "Cardiothoracic Surgery",
        "Neurosurgery",
        "Orthopedic Surgery",
        "Plastic & Reconstructive Surgery",
        "Pediatric Surgery",
        "Gynecology & Obstetrics",
        "Urology",
        "Otorhinolaryngology (ENT)",
        "Ophthalmic Surgery",
        "Vascular Surgery",
        "Oral & Maxillofacial Surgery",
        "Colorectal Surgery",
        "Surgical Oncology",
        "Trauma Surgery",
        "Transplant Surgery",
        "Bariatric Surgery",
        "Endocrine Surgery"
    ]
    create_field("Specialization / Surgery Type", spec_var, "combo", surgery_types)

    create_field("Mobile Number", mobile_var)
    
    # 3. UPDATED AVAILABILITY STATUS
    create_field("Current Status", avail_var, "combo", 
                 ["Available", "Off Duty", "On Surgery", "Not Available"])

    # Action Buttons
    btn_frame = Frame(form_frame, bg="white")
    btn_frame.pack(fill=X, padx=20, pady=30)
    
    Button(btn_frame, text="Add Doctor", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=10, command=add_doctor).pack(fill=X, pady=5)
    
    row_btns = Frame(btn_frame, bg="white")
    row_btns.pack(fill=X)
    Button(row_btns, text="Update", bg="#F59E0B", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=10, width=18, command=update_doctor).pack(side=LEFT)
    Button(row_btns, text="Delete", bg="#DC2626", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=10, width=18, command=delete_doctor).pack(side=RIGHT)
    Button(btn_frame, text="Clear Form", bg="#94A3B8", fg="white", bd=0, pady=5, command=clear_form).pack(fill=X, pady=10)

    # RIGHT: Data Table
    table_frame = Frame(content, bg="white")
    table_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    # Scrollbar
    sb = Scrollbar(table_frame)
    sb.pack(side=RIGHT, fill=Y)

    # Treeview Style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E2E8F0")
    style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))

    cols = ("ID", "Name", "Category", "Specialization", "Mobile", "Status")
    tree = ttk.Treeview(table_frame, columns=cols, show='headings', yscrollcommand=sb.set)
    
    # Columns
    tree.heading("ID", text="ID")
    tree.column("ID", width=40)
    tree.heading("Name", text="Doctor Name")
    tree.column("Name", width=150)
    tree.heading("Category", text="Rank/Category")
    tree.column("Category", width=120)
    tree.heading("Specialization", text="Specialization")
    tree.column("Specialization", width=180) # Increased width for longer names
    tree.heading("Mobile", text="Contact")
    tree.column("Mobile", width=100)
    tree.heading("Status", text="Availability")
    tree.column("Status", width=100)

    tree.pack(fill=BOTH, expand=True)
    sb.config(command=tree.yview)
    
    tree.bind('<ButtonRelease-1>', get_selected_row)
    
    # Load Initial Data
    display_data()

    window.mainloop()

if __name__ == "__main__":
    Show_Doctor_Info()