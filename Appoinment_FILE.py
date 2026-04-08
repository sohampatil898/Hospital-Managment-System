from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
import sqlite3
import datetime
import page_after_login 

try:
    from tkcalendar import DateEntry
except ImportError:
    pass

def book_appointment(window):
    # 1. Clear existing widgets (Fixes flicker/overlay)
    for widget in window.winfo_children():
        widget.destroy()
        
    window.title("Book Appointments")
    window.state('zoomed')
    window.configure(bg='#F1F5F9')

    connector = sqlite3.connect('Hospital.db')
    cursor = connector.cursor()
    connector.execute(
        "CREATE TABLE IF NOT EXISTS APPOINTMENTS (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT, EMAIL TEXT, PHONE TEXT, GENDER TEXT, DOB TEXT, TIME TEXT)"
    )

    def display_records():
        tree.delete(*tree.get_children())
        curr = connector.execute('SELECT ID, NAME, EMAIL, PHONE, GENDER, DOB, TIME FROM APPOINTMENTS')
        for records in curr.fetchall():
            tree.insert('', END, values=records)

    def clear_fields():
        name_var.set('')
        email_var.set('')
        phone_var.set('')
        time_var.set('')
        try:
            dob_var.set_date(datetime.datetime.now().date())
        except: pass
        if tree.selection():
            tree.selection_remove(tree.selection())

    def on_tree_select(event):
        selected_item = tree.selection()
        if not selected_item: return
        
        values = tree.item(selected_item)['values']
        
        # values[0] is ID, fill rest
        name_var.set(values[1])
        email_var.set(values[2])
        phone_var.set(values[3])
        gender_var.set(values[4])
        
        try:
            date_obj = datetime.datetime.strptime(values[5], '%Y-%m-%d').date()
            dob_var.set_date(date_obj)
        except: pass
        
        time_var.set(values[6])

    def add_record():
        name = name_var.get()
        email = email_var.get()
        phone = phone_var.get()
        gender = gender_var.get()
        time_slot = time_var.get()
        try:
            dob = dob_var.get_date()
        except:
            dob = datetime.date.today()

        if not name or not phone:
            mb.showerror('Error', "Name and Phone are required!")
            return

        connector.execute(
            'INSERT INTO APPOINTMENTS (NAME, EMAIL, PHONE, GENDER, DOB, TIME) VALUES (?, ?, ?, ?, ?, ?)',
            (name, email, phone, gender, dob, time_slot)
        )
        connector.commit()
        mb.showinfo('Success', "Appointment Booked")
        display_records()
        clear_fields()

    def update_record():
        if not tree.selection():
            mb.showerror('Error', 'Please select an appointment to update')
            return
        
        current_item = tree.item(tree.selection())
        record_id = current_item['values'][0]
        
        try:
            dob = dob_var.get_date()
        except:
            dob = datetime.date.today()

        connector.execute(
            'UPDATE APPOINTMENTS SET NAME=?, EMAIL=?, PHONE=?, GENDER=?, DOB=?, TIME=? WHERE ID=?',
            (name_var.get(), email_var.get(), phone_var.get(), gender_var.get(), dob, time_var.get(), record_id)
        )
        connector.commit()
        mb.showinfo('Success', "Appointment Updated Successfully")
        display_records()
        clear_fields()

    def delete_record():
        if not tree.selection():
            mb.showerror('Error', 'Please select an appointment to delete')
            return
        
        if mb.askyesno('Confirm', 'Are you sure you want to delete this appointment?'):
            current_item = tree.item(tree.selection())
            record_id = current_item['values'][0]
            connector.execute('DELETE FROM APPOINTMENTS WHERE ID=?', (record_id,))
            connector.commit()
            display_records()
            clear_fields()

    # 2. Fixed Back Function
    def go_back():
        # Do NOT destroy the window
        # window.destroy() 
        
        # Pass the existing window back to the dashboard
        import page_after_login
        page_after_login.page_after_login(window)

    # --- GUI ---
    header_frame = Frame(window, bg="#1E293B", height=70)
    header_frame.pack(fill=X)
    Label(header_frame, text="Appointment Booking ", font=("Segoe UI", 20, "bold"), bg="#1E293B", fg="white").pack(side=LEFT, padx=20, pady=10)
    Button(header_frame, text="⬅ Back to Dashboard", bg="#EF4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5, cursor="hand2", command=go_back).pack(side=RIGHT, padx=20, pady=10)

    content = Frame(window, bg='#F1F5F9')
    content.pack(fill=BOTH, expand=True, padx=20, pady=20)

    form_frame = Frame(content, bg="white", width=350, relief=RIDGE, bd=1)
    form_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
    form_frame.pack_propagate(False)

    name_var = StringVar()
    email_var = StringVar()
    phone_var = StringVar()
    gender_var = StringVar(value="Male")
    time_var = StringVar()

    Label(form_frame, text="New Appointment", font=("Segoe UI", 14, "bold"), bg="white", fg="#334155").pack(pady=20)

    Label(form_frame, text="Patient Name", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=name_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Email Address", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=email_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Phone Number", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=phone_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Gender", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    ttk.Combobox(form_frame, textvariable=gender_var, values=["Male", "Female", "Other"], state="readonly").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Preferred Date", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    try:
        dob_var = DateEntry(form_frame, font=("Segoe UI", 10), bg="white", date_pattern='yyyy-mm-dd')
        dob_var.pack(fill=X, padx=20, pady=5)
    except:
        dob_var = Entry(form_frame)
        dob_var.pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Time (e.g., 10:30 AM)", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=time_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    btn_frame = Frame(form_frame, bg="white")
    btn_frame.pack(fill=X, padx=20, pady=20)

    Button(btn_frame, text="Book Appointment", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=add_record).pack(fill=X, pady=(0, 10))
    
    side_btns = Frame(btn_frame, bg="white")
    side_btns.pack(fill=X, pady=10)
    Button(side_btns, text="Update", bg="#F59E0B", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, width=15, command=update_record).pack(side=LEFT, padx=(0,5))
    Button(side_btns, text="Delete", bg="#DC2626", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, width=15, command=delete_record).pack(side=RIGHT, padx=(5,0))
    Button(btn_frame, text="Clear", bg="#94A3B8", fg="white", font=("Segoe UI", 10), bd=0, pady=5, command=clear_fields).pack(fill=X)

    tree_frame = Frame(content, bg="white", highlightbackground="#CBD5E1", highlightthickness=1)
    tree_frame.pack(side=LEFT, fill=BOTH, expand=True)

    tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Email', 'Phone', 'Gender', 'Date', 'Time'), show='headings')
    
    cols = ['ID', 'Name', 'Email', 'Phone', 'Gender', 'Date', 'Time']
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    tree.column('ID', width=40)
    tree.column('Name', width=150)
    tree.pack(fill=BOTH, expand=True)

    tree.bind('<<TreeviewSelect>>', on_tree_select)

    display_records()
    
    # 3. REMOVED window.mainloop() (Prevents freeze)

# 4. Fixed Test Block
if __name__ == "__main__":
    test_window = Tk()
    book_appointment(test_window)
    test_window.mainloop()