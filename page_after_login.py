from tkinter import *
from tkinter import ttk 
import sqlite3
import os
from datetime import date
import time
import calendar



def page_after_login(window):
    # --- WINDOW SETUP ---
    for widget in window.winfo_children():
        widget.destroy()
        
    window.title('Hospital Management System | Admin Dashboard')
    window.state('zoomed') 
    window.configure(bg='#F1F5F9')

    # --- COLOR PALETTE ---
    COLOR_SIDEBAR = "#0F172A"       
    COLOR_SIDEBAR_HOVER = "#1E293B" 
    COLOR_ACCENT = "#3B82F6"        
    COLOR_BG = "#F1F5F9"            
    COLOR_TEXT_MAIN = "#1E293B"     
    COLOR_TEXT_MUTED = "#64748B"    
    
    # --- DATABASE HELPERS ---
    def get_db_connection():
        if os.path.exists('Hospital.db'): return sqlite3.connect('Hospital.db')
        elif os.path.exists('hospital.db'): return sqlite3.connect('hospital.db')
        else: return sqlite3.connect('database1.db')

    def get_count(table_name):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            except:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}s") 
            val = cur.fetchone()[0]
            conn.close()
            return val
        except: return 0

    def get_earnings():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT SUM(AMOUNT) FROM BILLING WHERE STATUS='PAID'")
            val = cur.fetchone()[0]
            conn.close()
            return val if val else 0
        except: return 0

    # ---------------------------------------------------------
    # NEW: CONNECTED TO BED_FILE DATABASE
    # ---------------------------------------------------------
    def get_bed_stats(ward_name):
        # 1. Define Total Capacity for each ward 
        # (Since Bed_FILE.py only stores occupied beds, we assume these max totals)
        totals = {
            "General Ward": 50,
            "Private Room": 20,
            "ICU": 10
        }
        total_capacity = totals.get(ward_name, 20) # Default to 20 if name not found

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # 2. Count occupied beds from BED_MANAGEMENT table
            # We use the 'WARD' column as seen in your Bed_FILE.py
            cur.execute("SELECT COUNT(*) FROM BED_MANAGEMENT WHERE WARD=?", (ward_name,))
            occupied_count = cur.fetchone()[0]
            
            conn.close()
            return occupied_count, total_capacity
        except:
            # If table doesn't exist yet, return 0 occupied
            return 0, total_capacity

    # --- NAVIGATION FUNCTIONS (LAZY IMPORTS) ---
    def logout():
        for widget in window.winfo_children():
            widget.destroy()
        import Login_PAGE
        Login_PAGE.LoginPage(window) # Go back to Login

    def open_doctors():
        import Doctor_info
        Doctor_info.Show_Doctor_Info(window)

    def open_patients():
        import AddPatients
        AddPatients.add_patient(window)

    def open_appointments():
        import Appoinment_FILE
        Appoinment_FILE.book_appointment(window)

    def open_billing():
        import Billing_FILE
        Billing_FILE.open_billing(window)

    def open_surgeries():
        import Surgery_FILE
        Surgery_FILE.open_surgery(window)

    def open_beds():
        import Bed_FILE
        Bed_FILE.open_beds(window)

    def open_operation_room():
        import Operation_room
        Operation_room.open_operation_room(window)
    # --- LAYOUT: SIDEBAR ---
    sidebar = Frame(window, bg=COLOR_SIDEBAR, width=280)
    sidebar.pack(side=LEFT, fill=Y)
    sidebar.pack_propagate(False)

    # Profile Section
    profile_frame = Frame(sidebar, bg=COLOR_SIDEBAR, pady=40)
    profile_frame.pack(fill=X)
    cv_profile = Canvas(profile_frame, width=80, height=80, bg=COLOR_SIDEBAR, highlightthickness=0)
    cv_profile.pack()
    cv_profile.create_oval(5, 5, 75, 75, fill="#1E293B", outline=COLOR_ACCENT, width=2)
    cv_profile.create_text(40, 40, text="A", fill="white", font=("Arial", 30, "bold"))
    Label(profile_frame, text="Administrator", font=("Segoe UI", 14, "bold"), bg=COLOR_SIDEBAR, fg="white").pack(pady=(10, 0))

    # Menu Buttons
    def menu_btn(text, icon, cmd):
        btn_frame = Frame(sidebar, bg=COLOR_SIDEBAR)
        btn_frame.pack(fill=X, pady=2)
        btn = Button(btn_frame, text=f"   {icon}   {text}", font=("Segoe UI", 11), 
                     bg=COLOR_SIDEBAR, fg="#CBD5E1", activebackground=COLOR_SIDEBAR_HOVER, activeforeground="white",
                     bd=0, anchor="w", padx=30, pady=12, cursor="hand2", command=cmd)
        btn.pack(fill=X)
        btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_SIDEBAR_HOVER, fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_SIDEBAR, fg="#CBD5E1"))

    Label(sidebar, text="MAIN MENU", bg=COLOR_SIDEBAR, fg="#64748B", font=("Segoe UI", 8, "bold"), anchor="w").pack(fill=X, padx=30, pady=(30,10))
    menu_btn("Dashboard", "📊", None)
    menu_btn("Doctors", "👨‍⚕️", open_doctors)
    menu_btn("Patients", "👥", open_patients)
    menu_btn("Appointments", "📅", open_appointments)
    menu_btn("Billing", "💰", open_billing)
    
    Label(sidebar, text="MANAGEMENT", bg=COLOR_SIDEBAR, fg="#64748B", font=("Segoe UI", 8, "bold"), anchor="w").pack(fill=X, padx=30, pady=(20,10))
    menu_btn("Surgeries", "🏥", open_surgeries)
    menu_btn("Beds/Wards", "🛏", open_beds)
    menu_btn("Operation Room", "⚡", open_operation_room) 
    
    Button(sidebar, text="🚪 Log Out", font=("Segoe UI", 11, "bold"), bg="#EF4444", fg="white", 
           bd=0, pady=15, cursor="hand2", command=logout).pack(side=BOTTOM, fill=X)

    # --- LAYOUT: MAIN CONTENT ---
    main = Frame(window, bg=COLOR_BG)
    main.pack(side=LEFT, fill=BOTH, expand=True, padx=40, pady=40)

    # Header
    header = Frame(main, bg=COLOR_BG)
    header.pack(fill=X, pady=(0, 30))
    Label(header, text="Dashboard Overview", font=("Segoe UI", 26, "bold"), bg=COLOR_BG, fg=COLOR_TEXT_MAIN).pack(side=LEFT)

    # Stats Cards
    stats_frame = Frame(main, bg=COLOR_BG)
    stats_frame.pack(fill=X)
    for i in range(4): stats_frame.columnconfigure(i, weight=1)

    def draw_card(col, title, value, icon, color):
        card = Frame(stats_frame, bg="white", height=140)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        card.pack_propagate(False)
        Frame(card, bg=color, height=4).pack(side=BOTTOM, fill=X)
        Label(card, text=title.upper(), font=("Segoe UI", 9, "bold"), bg="white", fg=COLOR_TEXT_MUTED).place(x=20, y=20)
        Label(card, text=str(value), font=("Segoe UI", 24, "bold"), bg="white", fg=COLOR_TEXT_MAIN).place(x=20, y=45)
        cv = Canvas(card, width=50, height=50, bg="white", highlightthickness=0)
        cv.place(relx=1.0, y=35, x=-60)
        cv.create_oval(2, 2, 48, 48, outline=color, width=2)
        cv.create_text(25, 25, text=icon, font=("Arial", 20))

    draw_card(0, "Total Doctors", get_count('doctors'), "💼", "#3B82F6")
    draw_card(1, "Patients", get_count('patients'), "👥", "#10B981")
    draw_card(2, "Surgeries", get_count('surgery'), "🏥", "#EF4444")
    draw_card(3, "Revenue", f"${get_earnings():,.0f}", "💰", "#F59E0B")

    # --- BOTTOM SECTION ---
    bottom_frame = Frame(main, bg=COLOR_BG)
    bottom_frame.pack(fill=BOTH, expand=True, pady=30)
    
    # 1. RIGHT SIDE: CLOCK & CALENDAR (Fixed Width)
    widget_area = Frame(bottom_frame, bg=COLOR_BG, width=280)
    widget_area.pack(side=RIGHT, fill=Y, padx=(20,0))
    
    # 2. MIDDLE SIDE: BED STATUS (Fixed Width)
    bed_area = Frame(bottom_frame, bg="white", width=280, padx=20, pady=20)
    bed_area.pack(side=RIGHT, fill=Y)
    bed_area.pack_propagate(False)

    Label(bed_area, text="🛏 Bed Status", font=("Segoe UI", 12, "bold"), bg="white", fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 20))

    def draw_bed_progress(name, color):
        # Fetch stats using the new connected function
        occupied, total = get_bed_stats(name) 
        
        # Calculate percentage for bar
        pct = (occupied / total) * 100 if total > 0 else 0
        if pct > 100: pct = 100 # Cap at 100%

        frame = Frame(bed_area, bg="white")
        frame.pack(fill=X, pady=10)
        
        # Text Header
        header_f = Frame(frame, bg="white")
        header_f.pack(fill=X)
        Label(header_f, text=name, font=("Segoe UI", 10, "bold"), bg="white", fg="#475569").pack(side=LEFT)
        Label(header_f, text=f"{occupied}/{total}", font=("Segoe UI", 10, "bold"), bg="white", fg=color).pack(side=RIGHT)
        
        # Progress Bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(f"{name}.Horizontal.TProgressbar", foreground=color, background=color, troughcolor="#F1F5F9", borderwidth=0)
        
        pb = ttk.Progressbar(frame, style=f"{name}.Horizontal.TProgressbar", orient=HORIZONTAL, length=100, mode='determinate', value=pct)
        pb.pack(fill=X, pady=(5,0))

    # Calls using exact names from your Bed_FILE.py
    draw_bed_progress("General Ward", "#3B82F6") # Blue
    draw_bed_progress("ICU", "#EF4444")          # Red
    draw_bed_progress("Private Room", "#10B981") # Green

    # 3. LEFT SIDE: RECENT APPOINTMENTS (Takes remaining space)
    appt_area = Frame(bottom_frame, bg="white", padx=20, pady=20)
    appt_area.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 20))
    
    Label(appt_area, text="📋 Recent Appointments", font=("Segoe UI", 14, "bold"), bg="white", fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 10))
    
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#F1F5F9", borderwidth=0)
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=30, borderwidth=0)
    
    tree = ttk.Treeview(appt_area, columns=("Name", "Phone", "Time"), show="headings", height=5)
    tree.heading("Name", text="Patient Name")
    tree.heading("Phone", text="Contact")
    tree.heading("Time", text="Time")
    tree.column("Name", width=150)
    tree.pack(fill=BOTH, expand=True)
    
    try:
        conn = get_db_connection()
        try:
            rows = conn.execute("SELECT NAME, PHONE, TIME FROM appointments ORDER BY ID DESC LIMIT 8").fetchall()
        except:
            rows = conn.execute("SELECT NAME, MOBILE, TIME FROM appointment ORDER BY ID DESC LIMIT 8").fetchall()
        conn.close()
        for r in rows: tree.insert('', END, values=r)
    except:
        tree.insert('', END, values=("No Appointments", "-", "-"))

    # --- WIDGET AREA CONTENT (CLOCK & CALENDAR) ---
    # CLOCK
    clock_card = Frame(widget_area, bg="#1E293B", padx=20, pady=20)
    clock_card.pack(fill=X, pady=(0, 20))
    lbl_time = Label(clock_card, text="12:00:00", font=("Arial", 28, "bold"), bg="#1E293B", fg="white")
    lbl_time.pack()
    lbl_ampm = Label(clock_card, text="AM", font=("Arial", 12), bg="#1E293B", fg="#94A3B8")
    lbl_ampm.pack()
    
    def update_clock():
        lbl_time.config(text=time.strftime("%I:%M:%S"))
        lbl_ampm.config(text=time.strftime("%p"))
        window.after(1000, update_clock)
    update_clock()

    # CALENDAR
    cal_card = Frame(widget_area, bg="white", padx=20, pady=20)
    cal_card.pack(fill=BOTH, expand=True)
    
    now = date.today()
    Label(cal_card, text=f"{now.strftime('%B %Y')}", font=("Segoe UI", 12, "bold"), bg="white", fg=COLOR_TEXT_MAIN).pack(pady=(0, 10))
    
    cal_grid = Frame(cal_card, bg="white")
    cal_grid.pack()
    
    days_header = ["M", "T", "W", "T", "F", "S", "S"]
    for i, d in enumerate(days_header):
        Label(cal_grid, text=d, font=("Segoe UI", 10, "bold"), bg="white", fg="#94A3B8", width=4).grid(row=0, column=i)
    
    month_days = calendar.monthrange(now.year, now.month)[1]
    start_day = date(now.year, now.month, 1).weekday()
    
    row, col = 1, start_day
    for d in range(1, month_days + 1):
        bg_col, fg_col = ("white", COLOR_TEXT_MAIN)
        if d == now.day: bg_col, fg_col = (COLOR_ACCENT, "white")
            
        Label(cal_grid, text=str(d), font=("Segoe UI", 10), bg=bg_col, fg=fg_col, width=4, height=2)\
            .grid(row=row, column=col, padx=2, pady=2)
        
        col += 1
        if col > 6: col, row = 0, row + 1

    window.mainloop()

if __name__ == "__main__":
    page_after_login()