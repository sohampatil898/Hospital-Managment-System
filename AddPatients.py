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

def add_patient(window):
    # 1. Clear existing widgets (Fixes the flickering/overlay issue)
    for widget in window.winfo_children():
        widget.destroy()
        
    window.title("Patient Management")
    window.state('zoomed')

    connector = sqlite3.connect('Hospital.db')
    cursor = connector.cursor()
    
    connector.execute(
        "CREATE TABLE IF NOT EXISTS PATIENTS (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT, GENDER TEXT, MOBILE TEXT, DOB TEXT, HISTORY TEXT, PRESCRIPTION TEXT)"
    )

    def display_records():
        tree.delete(*tree.get_children())
        curr = connector.execute('SELECT ID, NAME, GENDER, MOBILE, DOB, HISTORY, PRESCRIPTION FROM PATIENTS')
        for records in curr.fetchall():
            tree.insert('', END, values=records)

    def clear_fields():
        name_var.set('')
        gender_var.set('Male')
        mobile_var.set('')
        history_var.set('')
        presc_var.set('')
        try:
            dob_var.set_date(datetime.datetime.now().date())
        except: pass
        if tree.selection():
            tree.selection_remove(tree.selection())

    def on_tree_select(event):
        selected_item = tree.selection()
        if not selected_item: return
        
        values = tree.item(selected_item)['values']
        
        name_var.set(values[1])
        gender_var.set(values[2])
        mobile_var.set(values[3])
        
        try:
            date_obj = datetime.datetime.strptime(values[4], '%Y-%m-%d').date()
            dob_var.set_date(date_obj)
        except: 
            pass 
            
        history_var.set(values[5])
        presc_var.set(values[6])

    def add_record():
        name = name_var.get()
        gender = gender_var.get()
        mobile = mobile_var.get()
        history = history_var.get()
        presc = presc_var.get()
        try:
            dob = dob_var.get_date()
        except:
            dob = datetime.date.today()

        if not name or not mobile:
            mb.showerror('Error', "Name and Mobile are required!")
            return

        connector.execute(
            'INSERT INTO PATIENTS (NAME, GENDER, MOBILE, DOB, HISTORY, PRESCRIPTION) VALUES (?, ?, ?, ?, ?, ?)',
            (name, gender, mobile, dob, history, presc)
        )
        connector.commit()
        mb.showinfo('Success', "Patient Record Added")
        display_records()
        clear_fields()

    def update_record():
        if not tree.selection():
            mb.showerror('Error', 'Please select a record from the table first!')
            return
        
        current_item = tree.item(tree.selection())
        record_id = current_item['values'][0]
        
        try:
            dob = dob_var.get_date()
        except:
            dob = datetime.date.today()

        connector.execute(
            'UPDATE PATIENTS SET NAME=?, GENDER=?, MOBILE=?, DOB=?, HISTORY=?, PRESCRIPTION=? WHERE ID=?',
            (name_var.get(), gender_var.get(), mobile_var.get(), dob, history_var.get(), presc_var.get(), record_id)
        )
        connector.commit()
        mb.showinfo('Success', "Record Updated Successfully")
        display_records()
        clear_fields()

    def delete_record():
        if not tree.selection():
            mb.showerror('Error', 'Please select a record to delete')
            return
        
        if mb.askyesno('Confirm', 'Are you sure you want to delete this record?'):
            current_item = tree.item(tree.selection())
            record_id = current_item['values'][0]
            connector.execute('DELETE FROM PATIENTS WHERE ID=?', (record_id,))
            connector.commit()
            display_records()
            clear_fields()

    # 2. Corrected Back Function Name
    def back_to_menu():
        import page_after_login
        page_after_login.page_after_login(window)

    # --- GUI ---
    header_frame = Frame(window, bg="#1E293B", height=70)
    header_frame.pack(fill=X)
    Label(header_frame, text="Patient Management", font=("Segoe UI", 20, "bold"), bg="#1E293B", fg="white").pack(side=LEFT, padx=20, pady=10)
    
    # 3. Fixed command: 'go_back' changed to 'back_to_menu'
    Button(header_frame, text="⬅ Back to Dashboard", bg="#EF4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5, cursor="hand2", command=back_to_menu).pack(side=RIGHT, padx=20, pady=10)

    content = Frame(window, bg='#F1F5F9')
    content.pack(fill=BOTH, expand=True, padx=20, pady=20)

    form_frame = Frame(content, bg="white", width=350, relief=RIDGE, bd=1)
    form_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
    form_frame.pack_propagate(False)

    name_var = StringVar()
    gender_var = StringVar(value="Male")
    mobile_var = StringVar()
    history_var = StringVar()
    presc_var = StringVar()

    Label(form_frame, text="Add New Patient", font=("Segoe UI", 14, "bold"), bg="white", fg="#334155").pack(pady=20)

    Label(form_frame, text="Full Name", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=name_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Gender", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    ttk.Combobox(form_frame, textvariable=gender_var, values=["Male", "Female", "Other"], state="readonly").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Mobile Number", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=mobile_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Date of Birth", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    try:
        dob_var = DateEntry(form_frame, font=("Segoe UI", 10), bg="white", date_pattern='yyyy-mm-dd')
        dob_var.pack(fill=X, padx=20, pady=5)
    except:
        dob_var = Entry(form_frame)
        dob_var.pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Medical History", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=history_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    Label(form_frame, text="Prescription", font=("Segoe UI", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(form_frame, textvariable=presc_var, font=("Segoe UI", 10), bg="#F8FAFC").pack(fill=X, padx=20, pady=5)

    btn_frame = Frame(form_frame, bg="white")
    btn_frame.pack(fill=X, padx=20, pady=20)

    Button(btn_frame, text="Save Record", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=add_record).pack(fill=X, pady=(0, 10))
    
    side_btns = Frame(btn_frame, bg="white")
    side_btns.pack(fill=X, pady=10)
    Button(side_btns, text="Update", bg="#F59E0B", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, width=15, command=update_record).pack(side=LEFT)
    Button(side_btns, text="Delete", bg="#DC2626", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, width=15, command=delete_record).pack(side=RIGHT)
    
    Button(btn_frame, text="Clear Form", bg="#94A3B8", fg="white", font=("Segoe UI", 10), bd=0, pady=5, command=clear_fields).pack(fill=X)

    tree_frame = Frame(content, bg="white", highlightbackground="#CBD5E1", highlightthickness=1)
    tree_frame.pack(side=LEFT, fill=BOTH, expand=True)

    cols = ('ID', 'Name', 'Gender', 'Mobile', 'DOB', 'History', 'Prescription')
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
    
    for col in cols:
        tree.heading(col, text=col)

    tree.column('ID', width=40)
    tree.column('Name', width=150)
    
    tree.pack(fill=BOTH, expand=True)

    tree.bind('<<TreeviewSelect>>', on_tree_select)

    display_records()
    
    

# 5. Fixed testing block
if __name__ == "__main__":
    # This block allows you to run this file individually for testing
    test_window = Tk()
    add_patient(test_window)
    test_window.mainloop()