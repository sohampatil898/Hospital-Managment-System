from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import os
import random
import time

# NOTE: Removed top-level import to prevent circular import errors
# import page_after_login 

def open_operation_room(window):
    # 1. Clear the existing window
    for widget in window.winfo_children():
        widget.destroy()

    window.geometry('1280x720')
    window.state('zoomed')
    window.title("Operation Theater & Surgery Simulator")
    window.configure(bg='#1e1e1e')

    # --- DATABASE FUNCTIONS ---
    def get_db_connection():
        if os.path.exists('Hospital.db'): return sqlite3.connect('Hospital.db')
        elif os.path.exists('hospital.db'): return sqlite3.connect('hospital.db')
        else: return sqlite3.connect('database1.db')

    # Fetch scheduled surgeries from the main Surgery Dept
    def get_scheduled_surgeries():
        try:
            conn = get_db_connection()
            c = conn.cursor()
            # Try to fetch surgeries that are 'Scheduled'
            c.execute("SELECT patient_name, surgery_type FROM surgery WHERE status='Scheduled'")
            rows = c.fetchall()
            conn.close()
            return [f"{r[0]} ({r[1]})" for r in rows]
        except:
            return ["Test Patient (Heart Surgery)", "Demo User (Knee Replacement)"]

    # --- MEDICINE & COST LOGIC (UPDATED) ---
    def get_meds_info(surgery_type):
        st = surgery_type.lower()
        meds = []
        cost = 0

        if "heart" in st or "cardiac" in st:
            meds = ["Heparin (Blood Thinner)", "Atropine", "Epinephrine", "Amiodarone"]
            cost = 2000
        elif "knee" in st or "ortho" in st or "bone" in st:
            meds = ["Morphine (Pain Relief)", "Cefazolin (Antibiotic)", "Tramadol", "Ketorolac"]
            cost = 1500
        elif "brain" in st or "neuro" in st:
            meds = ["Mannitol (Pressure)", "Dexamethasone", "Phenytoin", "Propofol"]
            cost = 2500
        elif "append" in st or "stomach" in st:
            meds = ["Metronidazole", "Paracetamol IV", "Ondansetron", "Gentamicin"]
            cost = 600
        elif "eye" in st or "cataract" in st:
            meds = ["Tropicamide Drops", "Moxifloxacin", "Prednisolone", "Local Anesthesia"]
            cost = 800
        else:
            meds = ["General Anesthesia", "Ibuprofen", "Amoxicillin", "Saline Solution"]
            cost = 500
            
        return meds, cost

    # --- GAME LOGIC VARIABLES ---
    game_running = False
    progress_val = 0
    success_target_start = 0
    success_target_end = 0
    
    # --- UI FUNCTIONS ---
    def update_tools(event):
        """Auto-fill tools AND MEDICINES AND COST"""
        selection = patient_var.get()
        if "(" in selection:
            s_type = selection.split("(")[1].replace(")", "").strip().lower()
        else:
            s_type = "general"

        # 1. Automated Tool Selection Logic
        tools = []
        if "heart" in s_type or "cardiac" in s_type:
            tools = ["Heart-Lung Bypass", "Sternum Saw", "Defibrillator", "Scalpel #10"]
        elif "knee" in s_type or "ortho" in s_type or "bone" in s_type:
            tools = ["Arthroscopic Camera", "Bone Drill", "Titanium Screws", "Mallet"]
        elif "brain" in s_type or "neuro" in s_type:
            tools = ["Craniotome", "Microscope", "Bipolar Forceps", "Neuro-Nav System"]
        else:
            tools = ["Scalpel", "Forceps", "Sutures", "Anesthesia Machine"]
        
        tools_list.set("\n".join(f"• {t}" for t in tools))

        # 2. Automated Medicine & Price Logic (UPDATED)
        meds, cost = get_meds_info(s_type)
        # Display Cost at the top of the list
        meds_list.set(f"EST. COST: ${cost}\n" + "\n".join(f"• {m}" for m in meds))

    def start_simulation():
        """Starts the surgery mini-game"""
        nonlocal game_running, progress_val, success_target_start, success_target_end
        
        if patient_var.get() == "":
            mb.showerror("Error", "Please select a patient to operate on!")
            return

        # 1. Setup Game Area
        game_canvas.delete("all")
        game_btn.config(state=DISABLED)
        result_lbl.config(text="STATUS: SURGERY IN PROGRESS...", fg="yellow")
        
        # 2. Random Success Zone (The Green Zone)
        success_target_start = random.randint(150, 400)
        success_target_end = success_target_start + 100  # 100px wide success zone
        
        # Draw Zones
        # Background Bar
        game_canvas.create_rectangle(50, 100, 550, 150, fill="#333", outline="white")
        # Success Zone (Green)
        game_canvas.create_rectangle(success_target_start, 100, success_target_end, 150, fill="#00E676", outline="")
        game_canvas.create_text((success_target_start + success_target_end)/2, 125, text="CLICK HERE!", fill="black", font=("Arial", 10, "bold"))

        # 3. Start Moving Indicator
        game_running = True
        move_indicator(50) # Start at x=50

    def move_indicator(x_pos):
        nonlocal game_running
        if not game_running: return

        # Draw Indicator (Red Line)
        game_canvas.delete("indicator")
        game_canvas.create_line(x_pos, 90, x_pos, 160, fill="red", width=4, tags="indicator")

        # Move Logic
        if x_pos < 550:
            window.after(10, lambda: move_indicator(x_pos + 4)) # Speed of the bar
        else:
            # Missed the target
            finish_game(False)

    def stop_game():
        """Player clicks to stop the indicator"""
        nonlocal game_running
        if not game_running: return
        
        game_running = False
        
        # Get current indicator position
        coords = game_canvas.coords("indicator")
        if coords:
            current_x = coords[0]
            # Check if inside green zone
            if success_target_start <= current_x <= success_target_end:
                finish_game(True)
            else:
                finish_game(False)

    def finish_game(success):
        if success:
            result_lbl.config(text="OPERATION SUCCESSFUL! ✅", fg="#00E676")
            mb.showinfo("Success", "Surgery Completed Successfully!\nVitals are stable.")
        else:
            result_lbl.config(text="COMPLICATIONS DETECTED! ⚠️", fg="#FF5252")
            mb.showwarning("Failed", "The operation had complications.\nPatient needs ICU.")
        
        game_btn.config(state=NORMAL)

    def back_to_dashboard():
        # Import inside function to avoid circular dependency
        import page_after_login
        page_after_login.page_after_login(window)

    # --- GUI LAYOUT ---
    
    # Header
    header = Frame(window, bg="#121212", height=60)
    header.pack(fill=X)
    Label(header, text="🏥 Operation Theater Control Room", font=("Segoe UI", 18, "bold"), bg="#121212", fg="white").pack(side=LEFT, padx=20, pady=10)
    
    # Corrected Back Button Logic
    Button(header, text="Exit to Dashboard", bg="#CF6679", fg="white", bd=0, padx=15, 
           command=back_to_dashboard).pack(side=RIGHT, padx=20, pady=10)

    # Main Grid
    main = Frame(window, bg="#1e1e1e")
    main.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # LEFT PANEL: CONFIGURATION
    left_panel = Frame(main, bg="#2d2d2d", width=400, padx=20, pady=20)
    left_panel.pack(side=LEFT, fill=Y)
    
    Label(left_panel, text="📋 Pre-Op Setup", font=("Segoe UI", 16, "bold"), bg="#2d2d2d", fg="#BB86FC").pack(anchor=W, pady=(0, 20))

    # Patient Selector
    Label(left_panel, text="Select Patient & Surgery:", font=("Segoe UI", 10), bg="#2d2d2d", fg="white").pack(anchor=W)
    patient_var = StringVar()
    p_combo = ttk.Combobox(left_panel, textvariable=patient_var, values=get_scheduled_surgeries(), font=("Segoe UI", 11), state="readonly")
    p_combo.pack(fill=X, pady=(5, 15))
    p_combo.bind("<<ComboboxSelected>>", update_tools)

    # Staff Inputs
    Label(left_panel, text="Lead Surgeon Count:", font=("Segoe UI", 10), bg="#2d2d2d", fg="white").pack(anchor=W)
    Spinbox(left_panel, from_=1, to=5, font=("Segoe UI", 11)).pack(fill=X, pady=(5, 10))

    # Automated Tools Display
    Label(left_panel, text="🔧 Required Equipment (Auto):", font=("Segoe UI", 10, "bold"), bg="#2d2d2d", fg="#03DAC6").pack(anchor=W, pady=(15, 5))
    tools_list = StringVar(value="Select a surgery...")
    Label(left_panel, textvariable=tools_list, font=("Consolas", 10), bg="#333", fg="#E0E0E0", justify=LEFT, anchor="nw", height=5, width=35, relief=FLAT).pack(fill=X)

    # --- NEW: MEDICINES DISPLAY ---
    Label(left_panel, text="💊 Meds & Cost (Auto):", font=("Segoe UI", 10, "bold"), bg="#2d2d2d", fg="#CF6679").pack(anchor=W, pady=(15, 5))
    meds_list = StringVar(value="Select a surgery...")
    Label(left_panel, textvariable=meds_list, font=("Consolas", 10), bg="#333", fg="#E0E0E0", justify=LEFT, anchor="nw", height=6, width=35, relief=FLAT).pack(fill=X)
    # ------------------------------

    # RIGHT PANEL: SIMULATION (GAME)
    right_panel = Frame(main, bg="#1e1e1e")
    right_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=20)

    Label(right_panel, text="⚡ Surgical Interaction Module", font=("Segoe UI", 16, "bold"), bg="#1e1e1e", fg="white").pack(pady=20)

    # Game Canvas
    game_canvas = Canvas(right_panel, width=600, height=250, bg="#222", highlightthickness=0)
    game_canvas.pack(pady=20)
    
    # Instructions inside Canvas
    game_canvas.create_text(300, 125, text="Waiting to start...\nSelect a patient and click 'Begin Surgery'", fill="#777", font=("Arial", 14), justify=CENTER)

    # Result Label
    result_lbl = Label(right_panel, text="READY", font=("Segoe UI", 20, "bold"), bg="#1e1e1e", fg="#777")
    result_lbl.pack(pady=10)

    # Control Buttons
    btn_frame = Frame(right_panel, bg="#1e1e1e")
    btn_frame.pack(pady=20)

    game_btn = Button(btn_frame, text="▶ BEGIN SURGERY", font=("Segoe UI", 14, "bold"), bg="#3700B3", fg="white", 
                      padx=20, pady=10, bd=0, activebackground="#6200EE", activeforeground="white", command=start_simulation)
    game_btn.pack(side=LEFT, padx=10)

    # The "Action" Button for the game
    action_btn = Button(btn_frame, text="🛑 PERFORM ACTION (STOP)", font=("Segoe UI", 14, "bold"), bg="#03DAC6", fg="black", 
                        padx=20, pady=10, bd=0, command=stop_game)
    action_btn.pack(side=LEFT, padx=10)

    # REMOVED window.mainloop() so it doesn't freeze the app

if __name__ == "__main__":
    # Correct testing block
    test_window = Tk()
    open_operation_room(test_window)
    test_window.mainloop()