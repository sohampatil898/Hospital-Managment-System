from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import sqlite3
import os
import datetime

# Note: Import moved inside back function to prevent circular import errors
# import page_after_login

def open_billing(window):
    # 1. Clear existing widgets from the passed window
    for widget in window.winfo_children():
        widget.destroy()
        
    window.title('Billing System')
    window.geometry('1280x720')
    window.state('zoomed')
    window.configure(bg='#F1F5F9')

    # --- DATABASE CONNECTION ---
    def get_db_connection():
        if os.path.exists('Hospital.db'): return sqlite3.connect('Hospital.db')
        elif os.path.exists('hospital.db'): return sqlite3.connect('hospital.db')
        else: return sqlite3.connect('database1.db')

    connector = get_db_connection()
    
    # Create Table
    connector.execute("""CREATE TABLE IF NOT EXISTS BILLING (
        BILL_ID INTEGER PRIMARY KEY AUTOINCREMENT, 
        PATIENT TEXT, SERVICE TEXT, AMOUNT REAL, STATUS TEXT, DATE_GENERATED TEXT
    )""")

    try:
        connector.execute("ALTER TABLE BILLING ADD COLUMN DATE_GENERATED TEXT")
    except: pass 

    # --- VARIABLES ---
    # These must be defined after window is cleared but before functions use them
    p_name_var = StringVar()
    surgery_var = StringVar(value="0")
    med_var = StringVar(value="0")
    days_var = StringVar(value="1")
    ward_var = StringVar(value="General Ward")

    # --- FUNCTIONS ---

    def fetch_surgery_cost():
        name = p_name_var.get()
        if not name:
            mb.showerror("Error", "Please enter a Patient Name first.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT price, surgery_type FROM surgery WHERE patient_name LIKE ? ORDER BY ID DESC LIMIT 1", ('%' + name + '%',))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                surgery_price = row[0]
                surgery_type = row[1]
                surgery_var.set(str(surgery_price))
                
                # Auto-Calculate Medicine Cost based on surgery type
                st = surgery_type.lower()
                med_cost = 500 # Default
                
                if "heart" in st or "cardiac" in st: med_cost = 2000
                elif "brain" in st or "neuro" in st: med_cost = 2500
                elif "knee" in st or "ortho" in st: med_cost = 1500
                elif "eye" in st or "cataract" in st: med_cost = 800
                elif "append" in st or "stomach" in st: med_cost = 600
                
                med_var.set(str(med_cost))
                mb.showinfo("Found", f"Found: {surgery_type}\nSurgery Cost: ${surgery_price}\nAuto-Added Meds: ${med_cost}")
            else:
                mb.showerror("Not Found", "No surgery records found for this patient.")
                surgery_var.set("0")
                med_var.set("0")
        except Exception as e:
            print(e)

    def get_bed_price(ward_type):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PRICE_PER_DAY FROM BED_MANAGEMENT WHERE WARD=? LIMIT 1", (ward_type,))
            row = cursor.fetchone()
            conn.close()
            return float(row[0]) if row else 1000.0
        except: return 0.0

    def calculate_total():
        try:
            s_cost = float(surgery_var.get())
            m_cost = float(med_var.get())
            days = int(days_var.get())
            price = get_bed_price(ward_var.get())
            
            # Update labels to show breakdown before saving
            total = s_cost + (price * days) + m_cost
            lbl_total.config(text=f"${total:,.2f}")
            return total, (price * days), price, s_cost, m_cost
        except: return None, None, None, None, None

    def generate_bill():
        total, bed_total, rate, s_cost, m_cost = calculate_total()
        if total is None: return
        
        summary = f"Surgery (${s_cost}) + {days_var.get()} Days {ward_var.get()} (${bed_total}) + Meds (${m_cost})"
        today = datetime.date.today().strftime("%Y-%m-%d")

        connector.execute('INSERT INTO BILLING (PATIENT, SERVICE, AMOUNT, STATUS, DATE_GENERATED) VALUES (?,?,?,?,?)', 
                          (p_name_var.get(), summary, total, 'Pending', today))
        connector.commit()
        display_records()
        clear_form()
        mb.showinfo("Success", "Bill Generated Successfully!")

    def update_bill():
        if not tree.selection():
            mb.showerror("Error", "Please Select a bill from the table to Update.")
            return

        # Calculate new values from the left form
        total, bed_total, rate, s_cost, m_cost = calculate_total()
        if total is None:
            mb.showerror("Error", "Please fill the form with valid numbers first.")
            return

        # Get selected Bill ID
        current_item = tree.item(tree.selection())
        bill_id = current_item['values'][0]
        
        summary = f"Surgery (${s_cost}) + {days_var.get()} Days {ward_var.get()} (${bed_total}) + Meds (${m_cost})"
        
        try:
            connector.execute(
                "UPDATE BILLING SET PATIENT=?, SERVICE=?, AMOUNT=? WHERE BILL_ID=?", 
                (p_name_var.get(), summary, total, bill_id)
            )
            connector.commit()
            display_records()
            mb.showinfo("Success", "Bill Updated Successfully!")
        except Exception as e:
            mb.showerror("Error", str(e))

    def delete_bill():
        if not tree.selection():
            mb.showerror("Error", "Please Select a bill from the table to Delete.")
            return
        
        current_item = tree.item(tree.selection())
        bill_id = current_item['values'][0]
        
        confirm = mb.askyesno("Confirm Delete", f"Are you sure you want to delete Bill ID #{bill_id}?")
        if confirm:
            try:
                connector.execute("DELETE FROM BILLING WHERE BILL_ID=?", (bill_id,))
                connector.commit()
                display_records()
                mb.showinfo("Success", "Bill Deleted Successfully.")
            except Exception as e:
                mb.showerror("Error", str(e))

    def print_detailed_invoice():
        selected_item = tree.selection()
        if not selected_item:
            mb.showerror("Error", "Please SELECT a bill from the table to print.")
            return
        
        row_values = tree.item(selected_item)['values']
        bill_id = row_values[0]
        name = row_values[1]
        details = row_values[2]
        amount = row_values[3]
        status = row_values[4]
        date_gen = row_values[5]

        # --- DETAILED INVOICE WINDOW ---
        top = Toplevel(window)
        top.title(f"Invoice #{bill_id}")
        top.geometry("450x600")
        top.configure(bg="white")
        
        border = Frame(top, bg="white", highlightbackground="black", highlightthickness=2)
        border.pack(fill=BOTH, expand=True, padx=20, pady=20)

        Label(border, text="HOSPITAL MANAGEMENT SYSTEM", font=("Times New Roman", 16, "bold"), bg="white").pack(pady=(20, 5))
        Label(border, text="123 Health Avenue, Med City", font=("Arial", 10), bg="white").pack()
        
        Frame(border, bg="black", height=2).pack(fill=X, padx=20, pady=10)

        info_frame = Frame(border, bg="white")
        info_frame.pack(fill=X, padx=20)
        Label(info_frame, text=f"Bill No: #{bill_id}", font=("Arial", 10, "bold"), bg="white").pack(side=LEFT)
        Label(info_frame, text=f"Date: {date_gen}", font=("Arial", 10), bg="white").pack(side=RIGHT)

        Label(border, text=f"Patient: {name}", font=("Arial", 12, "bold"), bg="white", anchor=W).pack(fill=X, padx=20, pady=(20, 5))

        Frame(border, bg="black", height=1).pack(fill=X, padx=20, pady=5)
        Label(border, text="DESCRIPTION                         AMOUNT", font=("Courier", 10, "bold"), bg="white", anchor=W).pack(fill=X, padx=20)
        Frame(border, bg="black", height=1).pack(fill=X, padx=20, pady=5)

        desc_text = details.replace(" + ", "\n")
        
        detail_frame = Frame(border, bg="white")
        detail_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        Label(detail_frame, text=desc_text, font=("Courier", 10), bg="white", justify=LEFT, anchor=NW).pack(side=LEFT, fill=BOTH)
        Label(detail_frame, text=f"${amount}", font=("Courier", 10, "bold"), bg="white", anchor=NE).pack(side=RIGHT, anchor=NE)

        Frame(border, bg="black", height=2).pack(fill=X, padx=20, pady=10)
        
        total_frame = Frame(border, bg="white")
        total_frame.pack(fill=X, padx=20)
        Label(total_frame, text="GRAND TOTAL:", font=("Arial", 14, "bold"), bg="white").pack(side=LEFT)
        Label(total_frame, text=f"${amount}", font=("Arial", 14, "bold"), bg="white").pack(side=RIGHT)

        status_color = "green" if status == "PAID" else "red"
        Label(border, text=f"STATUS: {status}", font=("Arial", 12, "bold"), fg=status_color, bg="white").pack(pady=10)

    def mark_paid():
        if not tree.selection():
            mb.showerror("Error", "Please select a bill from the table to mark as paid.")
            return
        current_item = tree.item(tree.selection())
        bill_id = current_item['values'][0]
        try:
            connector.execute("UPDATE BILLING SET STATUS='PAID' WHERE BILL_ID=?", (bill_id,))
            connector.commit()
            display_records()
            mb.showinfo("Success", "Bill marked as PAID.")
        except Exception as e:
            mb.showerror("Error", str(e))

    def display_records():
        tree.delete(*tree.get_children())
        try:
            curr = connector.execute('SELECT BILL_ID, PATIENT, SERVICE, AMOUNT, STATUS, DATE_GENERATED FROM BILLING')
            for row in curr.fetchall():
                safe_row = [x if x is not None else "" for x in row]
                tree.insert('', END, values=safe_row)
        except: pass

    def clear_form():
        p_name_var.set("")
        surgery_var.set("0")
        med_var.set("0")
        days_var.set("1")
        lbl_total.config(text="$0.00")

    def on_tree_select(event):
        try:
            selected_item = tree.selection()
            if not selected_item: return
            row_values = tree.item(selected_item)['values']
            p_name_var.set(row_values[1]) # Auto-fill name
        except: pass

    def back():
        import page_after_login
        page_after_login.page_after_login(window)

    # --- GUI CONSTRUCTION (Using 'window' as parent) ---
    
    # Left Panel
    left = Frame(window, bg="white", width=400)
    left.pack(side=LEFT, fill=Y, padx=20, pady=20)
    
    Label(left, text="Billing System", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
    
    Label(left, text="Patient Name:", bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(left, textvariable=p_name_var).pack(fill=X, padx=20, pady=5)
    Button(left, text="Fetch Surgery & Med Cost", command=fetch_surgery_cost, bg="#1A73E8", fg="white").pack(anchor=E, padx=20, pady=5)
    
    Label(left, text="Surgery Cost ($):", bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(left, textvariable=surgery_var).pack(fill=X, padx=20, pady=5)
    
    Label(left, text="Medicine Cost (Auto-Filled):", bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(left, textvariable=med_var).pack(fill=X, padx=20, pady=5)
    
    Label(left, text="Ward Type:", bg="white", anchor=W).pack(fill=X, padx=20)
    OptionMenu(left, ward_var, "General Ward", "Private Room", "ICU", "Recovery Ward").pack(fill=X, padx=20, pady=5)
    
    Label(left, text="Days:", bg="white", anchor=W).pack(fill=X, padx=20)
    Entry(left, textvariable=days_var).pack(fill=X, padx=20, pady=5)
    
    Button(left, text="Calculate Total", command=calculate_total).pack(fill=X, padx=20, pady=10)

    lbl_total = Label(left, text="$0.00", font=("Arial", 20), bg="white", fg="green")
    lbl_total.pack(pady=10)
    
    # --- BUTTONS AREA ---
    Button(left, text="💾 Generate Bill", command=generate_bill, bg="#2196F3", fg="white", font=("Arial", 12, "bold")).pack(fill=X, padx=20, pady=(10, 5))
    
    # NEW: UPDATE BUTTON
    Button(left, text="🔄 Update Selected Record", command=update_bill, bg="#F59E0B", fg="white", font=("Arial", 11, "bold")).pack(fill=X, padx=20, pady=5)

    Button(left, text="🖨 Print Selected Invoice", command=print_detailed_invoice, bg="#607D8B", fg="white", font=("Arial", 11)).pack(fill=X, padx=20, pady=5)
    
    Button(left, text="Back", command=back).pack(side=BOTTOM, fill=X, padx=20, pady=20)

    # Right Panel (Treeview + Buttons)
    right_frame = Frame(window, bg='#F1F5F9')
    right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=20)
    
    # --- HEADER WITH BUTTONS ---
    header_frame = Frame(right_frame, bg='#F1F5F9')
    header_frame.pack(fill=X, pady=(0, 10))
    
    Label(header_frame, text="Billing History", font=("Segoe UI", 14, "bold"), bg='#F1F5F9').pack(side=LEFT)
    
    # NEW: DELETE BUTTON (Red)
    Button(header_frame, text="🗑 Delete", bg="#EF4444", fg="white", font=("Segoe UI", 10, "bold"), 
           command=delete_bill).pack(side=RIGHT, padx=(10, 0))

    Button(header_frame, text="✓ Mark Selected as PAID", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), 
           command=mark_paid).pack(side=RIGHT)
    # ----------------------------------------
    
    tree_frame = Frame(right_frame, bg="white")
    tree_frame.pack(fill=BOTH, expand=True)
    
    cols = ('ID', 'Patient', 'Details', 'Amount', 'Status', 'Date')
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
    
    tree.heading('ID', text='ID')
    tree.heading('Patient', text='Patient Name')
    tree.heading('Details', text='Service Breakdown')
    tree.heading('Amount', text='Total ($)')
    tree.heading('Status', text='Payment Status')
    tree.heading('Date', text='Date')

    tree.column('ID', width=40)
    tree.column('Patient', width=120)
    tree.column('Details', width=200)
    tree.column('Amount', width=80)
    tree.column('Status', width=80)
    tree.column('Date', width=100)

    tree.pack(fill=BOTH, expand=True)
    
    # Bind click to fill form (Optional)
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    display_records()
    # REMOVED main.mainloop() to prevent freeze

if __name__ == "__main__":
    # Standard testing block
    test_window = Tk()
    open_billing(test_window)
    test_window.mainloop()