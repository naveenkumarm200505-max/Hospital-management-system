import os
import sqlite3
from tkinter import messagebox, ttk
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

DB_FILE = "hospital.db"


def connect_db():
    try:
        return sqlite3.connect(DB_FILE)
    except Exception as e:
        messagebox.showerror(
            "Database Error", f"Cannot open local SQLite database\n{e}"
        )
        return None


def create_tables():
    conn = connect_db()
    if not conn:
        return
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS username_table(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment_table(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                age TEXT,
                phone TEXT,
                appointment_date TEXT,
                appointment_time TEXT,
                problem TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS doctor_table(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)

        cur.execute("SELECT COUNT(*) FROM username_table")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute(
                "INSERT INTO username_table (username, password) VALUES ('admin', '1234')"
            )
            conn.commit()
    except Exception as e:
        messagebox.showerror("Database Initialization Error", str(e))
    finally:
        if cur:
            cur.close()
        conn.close()


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("1100x760")
        self.resizable(True, True)
        self.current_user = None

        self.login_frame = LoginFrame(self)
        self.home_frame = HomeFrame(self)
        self.appointment_frame = AppointmentFrame(self)
        self.doctor_frame = DoctorFrame(self)
        self.view_frame = ViewDataFrame(self)

        self.show_login()

    def show_login(self):
        self.home_frame.pack_forget()
        self.appointment_frame.pack_forget()
        self.doctor_frame.pack_forget()
        self.view_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def show_home(self, username):
        self.current_user = username
        self.login_frame.pack_forget()
        self.appointment_frame.pack_forget()
        self.doctor_frame.pack_forget()
        self.view_frame.pack_forget()
        self.home_frame.set_user(username)
        self.home_frame.pack(fill="both", expand=True)

    def show_appointment(self):
        self.login_frame.pack_forget()
        self.home_frame.pack_forget()
        self.doctor_frame.pack_forget()
        self.view_frame.pack_forget()
        self.appointment_frame.set_user(self.current_user)
        self.appointment_frame.pack(fill="both", expand=True)

    def show_doctor_module(self):
        self.login_frame.pack_forget()
        self.home_frame.pack_forget()
        self.appointment_frame.pack_forget()
        self.view_frame.pack_forget()
        self.doctor_frame.refresh_table()
        self.doctor_frame.pack(fill="both", expand=True)

    def show_view_module(self):
        self.login_frame.pack_forget()
        self.home_frame.pack_forget()
        self.appointment_frame.pack_forget()
        self.doctor_frame.pack_forget()
        self.view_frame.refresh_all_views()
        self.view_frame.pack(fill="both", expand=True)


class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.parent = parent

        self.main_frame = ctk.CTkFrame(self, corner_radius=22)
        self.main_frame.place(
            relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.72
        )

        self.left_frame = ctk.CTkFrame(self.main_frame, corner_radius=18)
        self.left_frame.pack(
            side="left", fill="both", expand=True, padx=(20, 10), pady=20
        )

        self.right_frame = ctk.CTkFrame(self.main_frame, corner_radius=18)
        self.right_frame.pack(
            side="right", fill="both", expand=True, padx=(10, 20), pady=20
        )

        ctk.CTkLabel(
            self.left_frame,
            text="HOSPITAL\nMANAGEMENT\nSYSTEM",
            font=("Arial", 28, "bold"),
            justify="center",
        ).pack(pady=(60, 20))
        ctk.CTkLabel(
            self.left_frame,
            text="Offline Patient Care & Administration Portal",
            font=("Arial", 14),
        ).pack(pady=10)

        ctk.CTkLabel(
            self.right_frame, text="USER LOGIN", font=("Arial", 24, "bold")
        ).pack(pady=(40, 20))

        self.entry_username = ctk.CTkEntry(
            self.right_frame, width=320, height=42, placeholder_text="Username"
        )
        self.entry_username.pack(pady=10)

        self.entry_password = ctk.CTkEntry(
            self.right_frame,
            width=320,
            height=42,
            placeholder_text="Password",
            show="•",
        )
        self.entry_password.pack(pady=10)

        self.btn_toggle = ctk.CTkButton(
            self.right_frame,
            text="Show",
            width=80,
            height=34,
            command=self.toggle_password,
        )
        self.btn_toggle.pack(pady=(0, 10))

        ctk.CTkButton(
            self.right_frame, text="LOGIN", height=42, command=self.login_user
        ).pack(pady=6)
        ctk.CTkButton(
            self.right_frame,
            text="SIGN UP",
            height=42,
            command=self.open_signup,
        ).pack(pady=6)
        ctk.CTkButton(
            self.right_frame, text="CLEAR", height=42, command=self.clear_fields
        ).pack(pady=6)
        ctk.CTkButton(
            self.right_frame,
            text="EXIT",
            height=42,
            fg_color="#d9534f",
            command=self.parent.destroy,
        ).pack(pady=6)

    def login_user(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        conn = connect_db()
        if not conn:
            return

        cur = None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, username FROM username_table
                WHERE username=? AND password=?
            """,
                (username, password),
            )
            row = cur.fetchone()
            if row:
                messagebox.showinfo(
                    "Success", f"Welcome {username}!\nLogin Successful"
                )
                self.parent.show_home(username)
            else:
                messagebox.showerror("Error", "Invalid Username or Password!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cur:
                cur.close()
            conn.close()

    def clear_fields(self):
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.entry_username.focus_set()

    def toggle_password(self):
        if self.entry_password.cget("show") == "•":
            self.entry_password.configure(show="")
            self.btn_toggle.configure(text="Hide")
        else:
            self.entry_password.configure(show="•")
            self.btn_toggle.configure(text="Show")

    def open_signup(self):
        signup = ctk.CTkToplevel(self)
        signup.title("Sign Up")
        signup.geometry("420x420")
        signup.resizable(True, True)
        signup.grab_set()
        signup.after(100, signup.lift)

        frame = ctk.CTkFrame(signup, corner_radius=18)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(
            frame, text="CREATE ACCOUNT", font=("Arial", 22, "bold")
        ).pack(pady=(15, 5))

        e_user = ctk.CTkEntry(frame, width=280, height=40, placeholder_text="Username")
        e_user.pack(pady=8)

        e_pass = ctk.CTkEntry(
            frame, width=280, height=40, placeholder_text="Password", show="•"
        )
        e_pass.pack(pady=8)

        e_conf = ctk.CTkEntry(
            frame,
            width=280,
            height=40,
            placeholder_text="Confirm Password",
            show="•",
        )
        e_conf.pack(pady=8)

        e_key = ctk.CTkEntry(
            frame,
            width=280,
            height=40,
            placeholder_text="Admin Security Key",
            show="•",
        )
        e_key.pack(pady=8)

        def register_user():
            u = e_user.get().strip()
            p = e_pass.get().strip()
            c = e_conf.get().strip()
            key = e_key.get().strip()

            if not u or not p or not c or not key:
                messagebox.showwarning("Warning", "All fields are required!")
                return
            if p != c:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            if key != "9999":
                messagebox.showerror(
                    "Access Denied", "Invalid Admin Security Key!"
                )
                return

            conn = connect_db()
            if not conn:
                return

            cur = None
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id FROM username_table WHERE username=?", (u,)
                )
                if cur.fetchone():
                    messagebox.showerror("Error", "Username already exists!")
                    return
                cur.execute(
                    "INSERT INTO username_table (username, password) VALUES (?, ?)",
                    (u, p),
                )
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                signup.destroy()
            except Exception as ex:
                messagebox.showerror("Database Error", str(ex))
            finally:
                if cur:
                    cur.close()
                conn.close()

        ctk.CTkButton(
            frame, text="SIGN UP", height=40, command=register_user
        ).pack(pady=15)


class HomeFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.parent = parent
        self.username = "User"

        self.header = ctk.CTkFrame(self, height=80, corner_radius=0)
        self.header.pack(fill="x")

        self.title_lbl = ctk.CTkLabel(
            self.header,
            text="HOSPITAL MANAGEMENT SYSTEM",
            font=("Arial", 24, "bold"),
        )
        self.title_lbl.pack(pady=(15, 0))

        self.user_lbl = ctk.CTkLabel(self.header, text="", font=("Arial", 14))
        self.user_lbl.pack()

        self.body = ctk.CTkFrame(self, corner_radius=20)
        self.body.place(
            relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.75
        )

        ctk.CTkLabel(
            self.body, text="HOME DASHBOARD", font=("Arial", 26, "bold")
        ).pack(pady=15)
        ctk.CTkLabel(
            self.body, text="Select a module to continue", font=("Arial", 14)
        ).pack(pady=5)

        ctk.CTkButton(
            self.body,
            text="BOOK APPOINTMENT",
            height=45,
            width=240,
            command=self.parent.show_appointment,
        ).pack(pady=10)

        ctk.CTkButton(
            self.body,
            text="DOCTOR DIRECTORY",
            height=45,
            width=240,
            fg_color="#16a085",
            hover_color="#1abc9c",
            command=self.parent.show_doctor_module,
        ).pack(pady=10)

        ctk.CTkButton(
            self.body,
            text="VIEW REGISTERED DATA",
            height=45,
            width=240,
            fg_color="#8e44ad",
            hover_color="#9b59b6",
            command=self.parent.show_view_module,
        ).pack(pady=10)

        ctk.CTkButton(
            self.body,
            text="LOGOUT",
            height=45,
            width=240,
            fg_color="#d9534f",
            command=self.parent.show_login,
        ).pack(pady=10)

    def set_user(self, username):
        self.username = username
        self.user_lbl.configure(text=f"Welcome, {username}")


class AppointmentFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.parent = parent
        self.username = "User"

        ctk.CTkLabel(
            self, text="APPOINTMENT BOOKING", font=("Arial", 28, "bold")
        ).pack(pady=20)
        self.user_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.user_label.pack(pady=(0, 10))

        self.frame = ctk.CTkFrame(self, corner_radius=20)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)

        self.entry_patient = ctk.CTkEntry(
            self.frame, width=350, height=40, placeholder_text="Patient Name"
        )
        self.entry_patient.grid(row=0, column=0, padx=20, pady=15)

        self.entry_doctor = ctk.CTkEntry(
            self.frame, width=350, height=40, placeholder_text="Doctor Name"
        )
        self.entry_doctor.grid(row=0, column=1, padx=20, pady=15)

        self.entry_age = ctk.CTkEntry(
            self.frame, width=350, height=40, placeholder_text="Age"
        )
        self.entry_age.grid(row=1, column=0, padx=20, pady=15)

        self.entry_phone = ctk.CTkEntry(
            self.frame, width=350, height=40, placeholder_text="Phone Number"
        )
        self.entry_phone.grid(row=1, column=1, padx=20, pady=15)

        self.entry_date = ctk.CTkEntry(
            self.frame,
            width=350,
            height=40,
            placeholder_text="Appointment Date (YYYY-MM-DD)",
        )
        self.entry_date.grid(row=2, column=0, padx=20, pady=15)

        self.entry_time = ctk.CTkEntry(
            self.frame,
            width=350,
            height=40,
            placeholder_text="Appointment Time (HH:MM)",
        )
        self.entry_time.grid(row=2, column=1, padx=20, pady=15)

        ctk.CTkLabel(self.frame, text="Problem Description").grid(
            row=3, column=0, padx=20, pady=(15, 5), sticky="w"
        )
        self.text_problem = ctk.CTkTextbox(self.frame, width=760, height=180)
        self.text_problem.grid(row=4, column=0, columnspan=2, padx=20, pady=10)

        btn_frame = ctk.CTkFrame(self.frame, corner_radius=12)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="SAVE APPOINTMENT",
            command=self.save_appointment,
            width=200,
            height=40,
        ).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(
            btn_frame, text="CLEAR", command=self.clear_fields, width=140, height=40
        ).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(
            btn_frame, text="BACK", command=self.show_back, width=140, height=40
        ).grid(row=0, column=2, padx=10, pady=10)

    def set_user(self, username):
        self.username = username
        self.user_label.configure(text=f"Logged in as: {username}")

    def save_appointment(self):
        patient_name = self.entry_patient.get().strip()
        doctor_name = self.entry_doctor.get().strip()
        age = self.entry_age.get().strip()
        phone = self.entry_phone.get().strip()
        date = self.entry_date.get().strip()
        time = self.entry_time.get().strip()
        problem = self.text_problem.get("1.0", "end").strip()

        if not patient_name or not doctor_name or not phone or not date or not time:
            messagebox.showwarning("Warning", "Please fill all required fields!")
            return

        conn = connect_db()
        if not conn:
            return

        cur = None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO appointment_table
                (patient_name, doctor_name, age, phone, appointment_date, appointment_time, problem)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (patient_name, doctor_name, age, phone, date, time, problem),
            )
            conn.commit()
            messagebox.showinfo("Success", "Appointment booked successfully!")
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cur:
                cur.close()
            conn.close()

    def clear_fields(self):
        self.entry_patient.delete(0, "end")
        self.entry_doctor.delete(0, "end")
        self.entry_age.delete(0, "end")
        self.entry_phone.delete(0, "end")
        self.entry_date.delete(0, "end")
        self.entry_time.delete(0, "end")
        self.text_problem.delete("1.0", "end")

    def show_back(self):
        self.parent.show_home(self.username)


class DoctorFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.parent = parent

        ctk.CTkLabel(
            self, text="DOCTOR DIRECTORY MANAGEMENT", font=("Arial", 26, "bold")
        ).pack(pady=15)

        self.main_workplace = ctk.CTkFrame(self, corner_radius=15)
        self.main_workplace.pack(padx=20, pady=10, fill="both", expand=True)

        self.input_subframe = ctk.CTkFrame(self.main_workplace, fg_color="transparent")
        self.input_subframe.pack(fill="x", padx=20, pady=15)

        self.doc_name = ctk.CTkEntry(
            self.input_subframe, width=210, height=38, placeholder_text="Doctor Name"
        )
        self.doc_name.grid(row=0, column=0, padx=5, pady=5)

        self.doc_special = ctk.CTkEntry(
            self.input_subframe,
            width=210,
            height=38,
            placeholder_text="Specialization",
        )
        self.doc_special.grid(row=0, column=1, padx=5, pady=5)

        self.doc_phone = ctk.CTkEntry(
            self.input_subframe, width=210, height=38, placeholder_text="Phone No."
        )
        self.doc_phone.grid(row=0, column=2, padx=5, pady=5)

        self.doc_email = ctk.CTkEntry(
            self.input_subframe, width=210, height=38, placeholder_text="Email Address"
        )
        self.doc_email.grid(row=0, column=3, padx=5, pady=5)

        self.actions_pane = ctk.CTkFrame(self.main_workplace, fg_color="transparent")
        self.actions_pane.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            self.actions_pane,
            text="ADD DOCTOR",
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=140,
            height=36,
            command=self.add_doctor_record,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            self.actions_pane,
            text="CLEAR FIELDS",
            width=120,
            height=36,
            command=self.clear_form,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            self.actions_pane,
            text="BACK TO HOME",
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            width=130,
            height=36,
            command=self.back_to_dashboard,
        ).pack(side="right")

        ctk.CTkLabel(
            self.main_workplace, text="Registered Hospital Staff:", font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 2))

        self.table_view_wrapper = ttk.Frame(self.main_workplace)
        self.table_view_wrapper.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        self.tree = ttk.Treeview(
            self.table_view_wrapper,
            columns=("id", "name", "special", "phone", "email"),
            show="headings",
        )
        self.tree.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(
            self.table_view_wrapper, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(fill="y", side="right")

        headers = {
            "id": "DOC ID",
            "name": "DOCTOR NAME",
            "special": "SPECIALIZATION",
            "phone": "PHONE NUMBER",
            "email": "EMAIL ID",
        }
        for key, text in headers.items():
            self.tree.heading(key, text=text)
            self.tree.column(key, anchor="center", width=120)

    def add_doctor_record(self):
        name = self.doc_name.get().strip()
        spec = self.doc_special.get().strip()
        ph = self.doc_phone.get().strip()
        em = self.doc_email.get().strip()

        if not name or not spec:
            messagebox.showwarning(
                "Incomplete Input", "Doctor Name and Specialization are required fields!"
            )
            return

        conn = connect_db()
        if not conn:
            return
        cur = None
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO doctor_table (doctor_name, specialization, phone, email) VALUES (?, ?, ?, ?)",
                (name, spec, ph, em),
            )
            conn.commit()
            messagebox.showinfo(
                "Staff Updated", f"Successfully registered Dr. {name} into active roster."
            )
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Execution Error", str(e))
        finally:
            if cur:
                cur.close()
            conn.close()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = connect_db()
        if not conn:
            return
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, doctor_name, specialization, phone, email FROM doctor_table")
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            print(f"Error fetching directory lines: {e}")
        finally:
            if cur:
                cur.close()
            conn.close()

    def clear_form(self):
        self.doc_name.delete(0, "end")
        self.doc_special.delete(0, "end")
        self.doc_phone.delete(0, "end")
        self.doc_email.delete(0, "end")

    def back_to_dashboard(self):
        self.parent.show_home(self.parent.current_user)


class ViewDataFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.parent = parent

        ctk.CTkLabel(
            self, text="HOSPITAL DATA MASTER VIEW", font=("Arial", 26, "bold")
        ).pack(pady=15)

        self.panel_container = ctk.CTkFrame(self, corner_radius=15)
        self.panel_container.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_panel = ctk.CTkTabview(
            self.panel_container, segmented_button_selected_color="#8e44ad"
        )
        self.tab_panel.pack(fill="both", expand=True, padx=15, pady=(10, 15))

        self.tab_appointments = self.tab_panel.add("APPOINTMENTS RECORD")
        self.tab_doctors = self.tab_panel.add("DOCTOR DIRECTORY LIST")

        self.build_appointments_tab()
        self.build_doctors_tab()

        self.utilities_bar = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.utilities_bar.pack(fill="x", padx=25, pady=(5, 15))

        ctk.CTkButton(
            self.utilities_bar,
            text="UPDATE SELECTED RECORD",
            fg_color="#f39c12",
            hover_color="#e67e22",
            height=38,
            command=self.update_selected_record,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.utilities_bar,
            text="DELETE SELECTED RECORD",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=38,
            command=self.delete_selected_record,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.utilities_bar,
            text="REFRESH TABLES",
            fg_color="#2980b9",
            hover_color="#3498db",
            height=38,
            command=self.refresh_all_views,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.utilities_bar,
            text="BACK TO MAIN DASHBOARD",
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            height=38,
            command=self.exit_view,
        ).pack(side="right", padx=5)

    def build_appointments_tab(self):
        frame = ttk.Frame(self.tab_appointments)
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.appt_tree = ttk.Treeview(
            frame,
            columns=("id", "patient", "doctor", "age", "phone", "date", "time", "problem"),
            show="headings",
        )
        self.appt_tree.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.appt_tree.yview)
        self.appt_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(fill="y", side="right")

        headers = {
            "id": "ID",
            "patient": "PATIENT NAME",
            "doctor": "DOCTOR ASSIGNED",
            "age": "AGE",
            "phone": "PHONE NUMBER",
            "date": "DATE",
            "time": "TIME SLOT",
            "problem": "DIAGNOSIS NOTE",
        }
        for k, text in headers.items():
            self.appt_tree.heading(k, text=text)
            w = 150 if k in ("patient", "doctor", "problem") else 80
            self.appt_tree.column(k, anchor="center", width=w)

    def build_doctors_tab(self):
        frame = ttk.Frame(self.tab_doctors)
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.doc_tree = ttk.Treeview(
            frame, columns=("id", "name", "special", "phone", "email"), show="headings"
        )
        self.doc_tree.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(fill="y", side="right")

        headers = {
            "id": "DOC ID",
            "name": "DOCTOR NAME",
            "special": "SPECIALIZATION",
            "phone": "CONTACT NO",
            "email": "EMAIL ID",
        }
        for k, text in headers.items():
            self.doc_tree.heading(k, text=text)
            self.doc_tree.column(k, anchor="center", width=140)

    def get_active_selection(self):
        current_tab = self.tab_panel.get()
        if current_tab == "APPOINTMENTS RECORD":
            selected_item = self.appt_tree.selection()
            if selected_item:
                return "appointments", self.appt_tree, self.appt_tree.item(selected_item)
        else:
            selected_item = self.doc_tree.selection()
            if selected_item:
                return "doctors", self.doc_tree, self.doc_tree.item(selected_item)
        return None, None, None

    def delete_selected_record(self):
        target_type, tree_widget, item_data = self.get_active_selection()
        if not item_data:
            messagebox.showwarning("No Selection", "Please click on a row to delete first!")
            return

        values = item_data["values"]
        record_id = values[0]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete record ID {record_id}?"
        )

        if confirm:
            conn = connect_db()
            if not conn:
                return
            cur = None
            try:
                cur = conn.cursor()
                if target_type == "appointments":
                    cur.execute("DELETE FROM appointment_table WHERE id = ?", (record_id,))
                else:
                    cur.execute("DELETE FROM doctor_table WHERE id = ?", (record_id,))
                conn.commit()
                messagebox.showinfo("Deleted", "Record has been removed successfully.")
                self.refresh_all_views()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to execute row deletion: {e}")
            finally:
                if cur:
                    cur.close()
                conn.close()

    def update_selected_record(self):
        target_type, tree_widget, item_data = self.get_active_selection()
        if not item_data:
            messagebox.showwarning("No Selection", "Please click on a row to modify first!")
            return

        values = item_data["values"]
        record_id = values[0]

        editor = ctk.CTkToplevel(self)
        editor.title(f"Modify Record ID: {record_id}")
        editor.geometry("450x550")
        editor.resizable(False, False)
        editor.grab_set()
        editor.after(100, editor.lift)

        editor_frame = ctk.CTkFrame(editor, corner_radius=15)
        editor_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            editor_frame, text=f"EDIT {target_type.upper()} ENTRY", font=("Arial", 18, "bold")
        ).pack(pady=15)

        entries = {}

        if target_type == "appointments":
            fields = [
                ("Patient Name", values[1]), ("Doctor Name", values[2]),
                ("Age", values[3]), ("Phone", values[4]),
                ("Date", values[5]), ("Time", values[6])
            ]
            for label, val in fields:
                ctk.CTkLabel(editor_frame, text=label, font=("Arial", 12)).pack(anchor="w", padx=25)
                entry = ctk.CTkEntry(editor_frame, width=380, height=32)
                entry.insert(0, str(val))
                entry.pack(pady=(2, 8))
                entries[label] = entry

            ctk.CTkLabel(editor_frame, text="Problem Description", font=("Arial", 12)).pack(anchor="w", padx=25)
            prob_txt = ctk.CTkTextbox(editor_frame, width=380, height=80)
            prob_txt.insert("1.0", str(values[7]))
            prob_txt.pack(pady=(2, 8))
            entries["Problem"] = prob_txt

        else:
            fields = [
                ("Doctor Name", values[1]), ("Specialization", values[2]),
                ("Phone No", values[3]), ("Email Address", values[4])
            ]
            for label, val in fields:
                ctk.CTkLabel(editor_frame, text=label, font=("Arial", 12)).pack(anchor="w", padx=25)
                entry = ctk.CTkEntry(editor_frame, width=380, height=32)
                entry.insert(0, str(val))
                entry.pack(pady=(2, 8))
                entries[label] = entry

        def execute_update_query():
            conn = connect_db()
            if not conn:
                return
            cur = None
            try:
                cur = conn.cursor()
                if target_type == "appointments":
                    p_name = entries["Patient Name"].get().strip()
                    d_name = entries["Doctor Name"].get().strip()
                    age_val = entries["Age"].get().strip()
                    ph_val = entries["Phone"].get().strip()
                    dt_val = entries["Date"].get().strip()
                    tm_val = entries["Time"].get().strip()
                    pr_val = entries["Problem"].get("1.0", "end").strip()

                    cur.execute("""
                        UPDATE appointment_table SET
                        patient_name=?, doctor_name=?, age=?, phone=?, appointment_date=?, appointment_time=?, problem=?
                        WHERE id=?
                    """, (p_name, d_name, age_val, ph_val, dt_val, tm_val, pr_val, record_id))
                else:
                    doc_n = entries["Doctor Name"].get().strip()
                    spec_n = entries["Specialization"].get().strip()
                    phone_n = entries["Phone No"].get().strip()
                    email_n = entries["Email Address"].get().strip()

                    cur.execute("""
                        UPDATE doctor_table SET
                        doctor_name=?, specialization=?, phone=?, email=?
                        WHERE id=?
                    """, (doc_n, spec_n, phone_n, email_n, record_id))

                conn.commit()
                messagebox.showinfo("Success", "Record updated safely.")
                editor.destroy()
                self.refresh_all_views()
            except Exception as ex:
                messagebox.showerror("Update Error", str(ex))
            finally:
                if cur:
                    cur.close()
                conn.close()

        ctk.CTkButton(
            editor_frame,
            text="COMMIT CHANGES",
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=execute_update_query
        ).pack(pady=15)

    def refresh_all_views(self):
        for item in self.appt_tree.get_children():
            self.appt_tree.delete(item)
        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)

        conn = connect_db()
        if not conn:
            return
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, patient_name, doctor_name, age, phone, appointment_date, appointment_time, problem FROM appointment_table")
            for row in cur.fetchall():
                self.appt_tree.insert("", "end", values=row)

            cur.execute("SELECT id, doctor_name, specialization, phone, email FROM doctor_table")
            for row in cur.fetchall():
                self.doc_tree.insert("", "end", values=row)
        except Exception as e:
            print(f"Error synchronization tables view: {e}")
        finally:
            if cur:
                cur.close()
            conn.close()

    def exit_view(self):
        self.parent.show_home(self.parent.current_user)


if __name__ == "__main__":
    create_tables()
    app = App()
    app.mainloop()
