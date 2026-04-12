#HOSPIATL MANAGEMENT SYSTEM

It is a desktop application built using Python and Tkinter to manage hospital operations like patient records, appointments,surgeries and billing. It uses SQLite3 as a backend database for efficient data storage and retrieval through a simple user-friendly interface.

#Need to work on:
1. The password should be encrypted and the password field shouldn't be displayed in the admin panel.
2. User should not be allowed to register if he/she tries to provide the already registered email ID.
3. Architecture & Tech Stack Migration : Transition to a Web Application ,eparate UI from Logic (MVC Pattern): Right now, your database queries, logic, and GUI drawing are all mixed inside the same functions. Separating these into "Models" (database), "Views" (UI), and "Controllers" (logic) will make the code much easier to maintain.
4. Feature Enhancements :
Real Payment Gateway Integration: Instead of just a button that marks a bill as "PAID", integrate the Stripe or Razorpay API so the hospital can actually process credit cards directly through the billing module.

SMS & Email Automations: Integrate an API like Twilio or SendGrid. When an appointment is booked, the system should automatically text the patient a reminder 24 hours before their visit.

Replace the "Operation Game": The timing mini-game in your Operation_room.py is an incredibly creative and fun portfolio feature! However, for a real hospital system, this module should be replaced with an "Operation Theater Scheduler" that tracks real-world equipment inventory, anesthesia logs, and assigned surgical teams.

Exporting & Reporting: Add the ability to generate and download PDF invoices for patients, or export monthly hospital revenue and bed occupancy statistics to Excel (using libraries like reportlab or pandas).

#Prerequisites:-
1.Python 3.x: The user must have Python 3 installed on their computer.
2.Tkinter: This is Python's standard GUI library.
Note for Windows/Mac users: It comes pre-installed with Python.
Note for Linux users: They might need to install it manually via their terminal (e.g., sudo apt-get install python3-tk).
3.SQLite3: Comes pre-installed with Python. No extra downloads or server setups are required.

#Languages and Technologies used:-
1. Core Programming Language
Python (3.x): The entire application logic, backend operations, and window management are written in Python.

2. Graphical User Interface (GUI) / Frontend
Tkinter (tkinter): Python's standard built-in GUI library. It is used to create the main windows, buttons, frames, canvases (for the surgery simulator), and labels.

Tkinter TTK (tkinter.ttk): The themed widget set for Tkinter. Used to create modern, clean-looking tables (Treeview) for displaying database records, as well as dropdown menus (Combobox).

3. Database / Backend Storage
SQLite3 (sqlite3): A lightweight, serverless relational database built directly into Python. It is used to create local .db files (Hospital.db) to persistently store, update, and manage all records (Patients, Appointments, Doctors, Beds, Billing, etc.).

4. Standard Python Libraries (Built-in)
os: Used for checking if the database file already exists on the user's computer (os.path.exists()).

datetime & time: Used to generate the live digital clock, fetch current dates for billing/invoices, and calculate month ranges for the custom calendar.

calendar: Used in the dashboard module to logically build the custom visual calendar grid.

random: Used in the Operation_room.py simulator to randomize the placement of the "success zone" target during the surgery mini-game.

5. External / Third-Party Libraries
tkcalendar (Optional/Graceful Fallback): The code attempts to import DateEntry from tkcalendar to provide users with a visual pop-up calendar when selecting dates (like Date of Birth or Appointment dates). (Note: Your code uses a try...except ImportError block, meaning if the user doesn't have it installed, the app won't crash!)

Summary of Tech Stack:
Frontend: Python (Tkinter)

Backend: Python

Database: SQLite

Architecture: Desktop GUI Application (Monolithic)

#Steps to Run the Project on Your Machine:-
Step 1: Download the Project:
Step 2: Install Python
Ensure you have Python 3.x installed on your system. You can download it from python.org.
Note: Make sure to check the box that says "Add Python to PATH" during installation.
Step 3: Install Optional Dependencies (Recommended)
This project is built entirely using standard built-in Python libraries (tkinter, sqlite3, etc.), so no major installations are required!
However, for the best visual experience with date selection, it is recommended to install the tkcalendar module. Open your terminal or command prompt and run:
pip install tkcalendar
Step 4: Run the Application
Open your terminal or command prompt.
Navigate to the folder where you downloaded the project:cd path/to/your/project-folder
Run the main dashboard file:python page_after_login.py
Step 5: Database Setup (Automated!)
You do not need to install MySQL, PostgreSQL, or configure any database servers!
The very first time you run the app, the SQLite code will automatically create a Hospital.db file and generate all the required tables for you.
