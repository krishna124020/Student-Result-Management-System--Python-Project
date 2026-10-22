import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import os
import database

class StudentResultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Result Management System")
        self.root.geometry("1160x720")
        self.root.minsize(980, 620)

        # Initialize SQLite database
        database.initialize_database()

        # Styles & Theme
        self.setup_styles()

        # Header with branding and quick Criteria / Subject buttons
        self.create_header()

        # Main Layout: Two Panels
        self.main_container = ttk.Frame(self.root, padding=12)
        self.main_container.pack(fill="both", expand=True)

        self.build_left_form()
        self.build_right_table()

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding=(12, 4))
        self.status_bar.pack(side="bottom", fill="x")

        # Load initial data
        self.load_all_records()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Color Palette
        primary = "#1E293B"       # Slate Navy
        accent = "#2563EB"        # Royal Blue
        success_green = "#059669" # Emerald Green
        amber = "#D97706"         # Amber
        bg_color = "#F8FAFC"      # Clean Light Slate
        text_dark = "#0F172A"

        self.root.configure(bg=bg_color)
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_dark, font=("Segoe UI", 10))
        style.configure("TLabelframe", background=bg_color, font=("Segoe UI", 11, "bold"))
        style.configure("TLabelframe.Label", background=bg_color, foreground=primary, font=("Segoe UI", 11, "bold"))

        style.configure("Header.TLabel", font=("Segoe UI", 17, "bold"), foreground="white", background=primary)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground="#CBD5E1", background=primary)

        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E2E8F0")

        # Custom Buttons
        style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), background=accent, foreground="white")
        style.map("Accent.TButton", background=[("active", "#1D4ED8")])

        style.configure("Success.TButton", font=("Segoe UI", 9, "bold"), background=success_green, foreground="white")
        style.map("Success.TButton", background=[("active", "#047857")])

        style.configure("Warning.TButton", font=("Segoe UI", 9, "bold"), background=amber, foreground="white")
        style.map("Warning.TButton", background=[("active", "#B45309")])

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#1E293B", height=75)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Left Title Box
        title_box = tk.Frame(header_frame, bg="#1E293B")
        title_box.pack(side="left", padx=20, pady=10)

        title = ttk.Label(title_box, text="🎓 Student Result Management System", style="Header.TLabel")
        title.pack(anchor="w")

        subtitle = ttk.Label(title_box, text="Academic Performance Evaluation, Custom Grading Criteria & Marksheet Engine", style="SubHeader.TLabel")
        subtitle.pack(anchor="w")

        # Right Action Buttons (Criteria & Subject Setup)
        btn_box = tk.Frame(header_frame, bg="#1E293B")
        btn_box.pack(side="right", padx=20, pady=15)

        btn_criteria = tk.Button(
            btn_box, text="⚙️ Change Total Marks Criteria", bg="#2563EB", fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=5, cursor="hand2",
            command=self.open_criteria_settings_dialog
        )
        btn_criteria.pack(side="left", padx=6)

        btn_add_sub = tk.Button(
            btn_box, text="➕ Add Subject", bg="#059669", fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=5, cursor="hand2",
            command=self.open_add_subject_dialog
        )
        btn_add_sub.pack(side="left", padx=6)

    # ---------------- LEFT PANEL: STUDENT & SUBJECT MARKS ----------------
    def build_left_form(self):
        form_frame = ttk.LabelFrame(self.main_container, text=" Student Details & Subject Marks ", padding=12)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        # Personal Info Fields
        ttk.Label(form_frame, text="Roll Number:").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_roll = ttk.Entry(form_frame, width=22)
        self.entry_roll.grid(row=0, column=1, sticky="w", pady=3, padx=5)

        ttk.Label(form_frame, text="Student Name:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_name = ttk.Entry(form_frame, width=22)
        self.entry_name.grid(row=1, column=1, sticky="w", pady=3, padx=5)

        ttk.Label(form_frame, text="Class / Sem:").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_class = ttk.Entry(form_frame, width=22)
        self.entry_class.insert(0, "B.Tech Sem 5")
        self.entry_class.grid(row=2, column=1, sticky="w", pady=3, padx=5)

        ttk.Label(form_frame, text="Gender:").grid(row=3, column=0, sticky="w", pady=3)
        self.combo_gender = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], state="readonly", width=20)
        self.combo_gender.set("Male")
        self.combo_gender.grid(row=3, column=1, sticky="w", pady=3, padx=5)

        # Subject Section Header + Quick Add Button
        ttk.Separator(form_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 8))

        sub_header_frame = ttk.Frame(form_frame)
        sub_header_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        ttk.Label(sub_header_frame, text="Subjects & Marks:", font=("Segoe UI", 9, "bold")).pack(side="left")
        btn_quick_sub = ttk.Button(sub_header_frame, text="➕ Add Subject", command=self.open_add_subject_dialog)
        btn_quick_sub.pack(side="right")

        # Scrollable container for dynamic subjects
        self.subjects_canvas = tk.Canvas(form_frame, bg="#F8FAFC", highlightthickness=0, height=190, width=280)
        self.subjects_scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=self.subjects_canvas.yview)
        self.subjects_inner_frame = ttk.Frame(self.subjects_canvas)

        self.subjects_inner_frame.bind(
            "<Configure>",
            lambda e: self.subjects_canvas.configure(scrollregion=self.subjects_canvas.bbox("all"))
        )

        self.subjects_canvas.create_window((0, 0), window=self.subjects_inner_frame, anchor="nw")
        self.subjects_canvas.configure(yscrollcommand=self.subjects_scrollbar.set)

        self.subjects_canvas.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=2)
        self.subjects_scrollbar.grid(row=6, column=2, sticky="ns", pady=2)

        # Render subject entry rows
        self.subject_entries = {}
        self.render_subject_entries()

        # Action Buttons
        btn_box = ttk.Frame(form_frame)
        btn_box.grid(row=7, column=0, columnspan=2, pady=(15, 5))

        btn_add = ttk.Button(btn_box, text="➕ Add Result", style="Accent.TButton", command=self.add_record_action)
        btn_add.grid(row=0, column=0, padx=3, pady=3)

        btn_update = ttk.Button(btn_box, text="✏️ Update", command=self.update_record_action)
        btn_update.grid(row=0, column=1, padx=3, pady=3)

        btn_delete = ttk.Button(btn_box, text="🗑️ Delete", command=self.delete_record_action)
        btn_delete.grid(row=1, column=0, padx=3, pady=3)

        btn_clear = ttk.Button(btn_box, text="🧹 Clear Form", command=self.clear_form)
        btn_clear.grid(row=1, column=1, padx=3, pady=3)

    def render_subject_entries(self):
        """Builds input fields dynamically based on subjects in database."""
        for widget in self.subjects_inner_frame.winfo_children():
            widget.destroy()

        self.subject_entries.clear()
        subjects = database.get_subjects()

        for idx, sub in enumerate(subjects):
            name = sub["name"]
            max_m = sub["max_marks"]
            pass_m = sub["pass_marks"]

            lbl_text = f"{name} (/{max_m}):"
            if len(lbl_text) > 24:
                lbl_text = lbl_text[:22] + "..:"

            lbl = ttk.Label(self.subjects_inner_frame, text=lbl_text)
            lbl.grid(row=idx, column=0, sticky="w", pady=3)

            ent = ttk.Entry(self.subjects_inner_frame, width=8)
            ent.grid(row=idx, column=1, sticky="w", pady=3, padx=(8, 2))
            self.subject_entries[name] = (ent, max_m, pass_m)

            # Delete subject button if > 1 subject exists
            if len(subjects) > 1:
                btn_del_sub = tk.Button(
                    self.subjects_inner_frame, text="✕", fg="#DC2626", bg="#F8FAFC",
                    bd=0, font=("Segoe UI", 8, "bold"), cursor="hand2",
                    command=lambda s_name=name: self.delete_subject_action(s_name)
                )
                btn_del_sub.grid(row=idx, column=2, padx=2)

    def delete_subject_action(self, subject_name):
        confirm = messagebox.askyesno("Delete Subject", f"Remove subject '{subject_name}' from future entry forms?")
        if confirm:
            database.delete_subject(subject_name)
            self.render_subject_entries()

    # ---------------- RIGHT PANEL: RECORDS TABLE & ACTIONS ----------------
    def build_right_table(self):
        right_frame = ttk.Frame(self.main_container)
        right_frame.pack(side="right", fill="both", expand=True)

        # Search Bar + Criteria Output Indicator
        search_box = ttk.LabelFrame(right_frame, text=" Student Records & Search ", padding=8)
        search_box.pack(fill="x", pady=(0, 10))

        ttk.Label(search_box, text="Search Roll No or Name:").pack(side="left", padx=5)
        self.entry_search = ttk.Entry(search_box, width=22)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<Return>", lambda e: self.search_action())

        btn_search = ttk.Button(search_box, text="🔍 Search", command=self.search_action)
        btn_search.pack(side="left", padx=4)

        btn_reset = ttk.Button(search_box, text="🔄 Show All", command=self.load_all_records)
        btn_reset.pack(side="left", padx=4)

        # Table Display
        columns = ("RollNo", "Name", "Class", "Gender", "CriteriaOutput", "Percentage", "Grade", "Status")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("RollNo", text="Roll No")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Class", text="Class")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("CriteriaOutput", text="Total Marks / Output")
        self.tree.heading("Percentage", text="Percentage")
        self.tree.heading("Grade", text="Grade")
        self.tree.heading("Status", text="Result")

        self.tree.column("RollNo", width=65, anchor="center")
        self.tree.column("Name", width=155, anchor="w")
        self.tree.column("Class", width=100, anchor="center")
        self.tree.column("Gender", width=65, anchor="center")
        self.tree.column("CriteriaOutput", width=145, anchor="center")
        self.tree.column("Percentage", width=80, anchor="center")
        self.tree.column("Grade", width=60, anchor="center")
        self.tree.column("Status", width=70, anchor="center")

        scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(right_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side="top", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # Bottom Action Bar
        bottom_bar = ttk.Frame(right_frame, padding=(0, 10))
        bottom_bar.pack(fill="x")

        btn_marksheet = ttk.Button(bottom_bar, text="📄 View & Print Student Marksheet Card", style="Success.TButton", command=self.open_marksheet_modal)
        btn_marksheet.pack(side="left", padx=5)

        btn_edit_criteria = ttk.Button(bottom_bar, text="⚙️ Configure Output Criteria", command=self.open_criteria_settings_dialog)
        btn_edit_criteria.pack(side="right", padx=5)

    # ---------------- CONTROLLER METHODS ----------------

    def validate_inputs(self):
        roll = self.entry_roll.get().strip()
        name = self.entry_name.get().strip()
        c_name = self.entry_class.get().strip()
        gender = self.combo_gender.get().strip()

        if not roll or not name or not c_name:
            messagebox.showwarning("Missing Fields", "Roll Number, Name, and Class cannot be blank.")
            return None

        marks_dict = {}
        for sub_name, (ent, max_m, pass_m) in self.subject_entries.items():
            val = ent.get().strip()
            if not val:
                messagebox.showwarning("Incomplete Marks", f"Please enter marks for '{sub_name}'.")
                return None
            try:
                m_int = int(val)
                if m_int < 0 or m_int > max_m:
                    messagebox.showerror("Invalid Marks", f"Marks for '{sub_name}' must be between 0 and {max_m}.")
                    return None
                marks_dict[sub_name] = m_int
            except ValueError:
                messagebox.showerror("Invalid Input", f"Marks for '{sub_name}' must be a whole number.")
                return None

        return (roll, name, c_name, gender, marks_dict)

    def add_record_action(self):
        data = self.validate_inputs()
        if not data:
            return

        roll, name, c_name, gender, marks_dict = data
        success, msg = database.add_student_result(roll, name, c_name, gender, marks_dict)
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.load_all_records()
        else:
            messagebox.showerror("Error", msg)

    def update_record_action(self):
        data = self.validate_inputs()
        if not data:
            return

        roll, name, c_name, gender, marks_dict = data
        success, msg = database.update_student_result(roll, name, c_name, gender, marks_dict)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_all_records()
        else:
            messagebox.showerror("Error", msg)

    def delete_record_action(self):
        roll = self.entry_roll.get().strip()
        if not roll:
            messagebox.showwarning("Select Student", "Please select or enter the Roll Number of the student to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete result for Roll No: {roll}?")
        if confirm:
            success, msg = database.delete_student_result(roll)
            if success:
                messagebox.showinfo("Deleted", msg)
                self.clear_form()
                self.load_all_records()
            else:
                messagebox.showerror("Error", msg)

    def clear_form(self):
        self.entry_roll.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.combo_gender.set("Male")
        for ent, _, _ in self.subject_entries.values():
            ent.delete(0, "end")

    def load_all_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        records = database.get_all_results()
        pass_count = 0
        for r in records:
            if r["status"] == "PASS":
                pass_count += 1
            pct_str = f"{r['percentage']:.1f}%"
            self.tree.insert("", "end", values=(
                r["roll_no"], r["name"], r["class_name"], r["gender"],
                r["criteria_output"], pct_str, r["grade"], r["status"]
            ))

        total_students = len(records)
        fail_count = total_students - pass_count
        settings = database.get_settings()
        mode_label = settings.get("output_mode", "STANDARD")
        self.status_var.set(
            f"  Output Criteria: {mode_label}  |  Total Students: {total_students}  |  Passed: {pass_count}  |  Failed: {fail_count}  |  Ready"
        )

    def search_action(self):
        q = self.entry_search.get().strip()
        if not q:
            self.load_all_records()
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        records = database.search_results(q)
        for r in records:
            pct_str = f"{r['percentage']:.1f}%"
            self.tree.insert("", "end", values=(
                r["roll_no"], r["name"], r["class_name"], r["gender"],
                r["criteria_output"], pct_str, r["grade"], r["status"]
            ))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        roll_no = item["values"][0]

        student = database.get_student_by_roll(str(roll_no))
        if student:
            self.entry_roll.delete(0, "end")
            self.entry_roll.insert(0, student["roll_no"])

            self.entry_name.delete(0, "end")
            self.entry_name.insert(0, student["name"])

            self.entry_class.delete(0, "end")
            self.entry_class.insert(0, student["class_name"])

            self.combo_gender.set(student["gender"])

            saved_marks = student["marks"]
            for sub_name, (ent, _, _) in self.subject_entries.items():
                ent.delete(0, "end")
                if sub_name in saved_marks:
                    ent.insert(0, str(saved_marks[sub_name]))

    # ---------------- ➕ ADD SUBJECT DIALOG ----------------
    def open_add_subject_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Subject")
        win.geometry("380x250")
        win.resizable(False, False)
        win.grab_set()

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Subject Name:").grid(row=0, column=0, sticky="w", pady=6)
        entry_sname = ttk.Entry(frame, width=22)
        entry_sname.grid(row=0, column=1, pady=6)
        entry_sname.focus_set()

        ttk.Label(frame, text="Max Marks:").grid(row=1, column=0, sticky="w", pady=6)
        entry_max = ttk.Spinbox(frame, from_=10, to=500, width=10)
        entry_max.set(100)
        entry_max.grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Passing Marks:").grid(row=2, column=0, sticky="w", pady=6)
        entry_pass = ttk.Spinbox(frame, from_=5, to=200, width=10)
        entry_pass.set(35)
        entry_pass.grid(row=2, column=1, sticky="w", pady=6)

        def save_subject():
            name = entry_sname.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a subject name.", parent=win)
                return
            try:
                m_max = int(entry_max.get())
                m_pass = int(entry_pass.get())
                if m_pass >= m_max:
                    messagebox.showerror("Error", "Passing marks must be less than Maximum marks.", parent=win)
                    return
            except ValueError:
                messagebox.showerror("Error", "Marks must be integer values.", parent=win)
                return

            success, msg = database.add_subject(name, m_max, m_pass)
            if success:
                messagebox.showinfo("Subject Added", msg, parent=win)
                win.destroy()
                self.render_subject_entries()
            else:
                messagebox.showerror("Failed", msg, parent=win)

        btn_save = ttk.Button(frame, text="💾 Save Subject", style="Accent.TButton", command=save_subject)
        btn_save.grid(row=3, column=0, columnspan=2, pady=15)

    # ---------------- ⚙️ CRITERIA / SETTINGS MODAL ----------------
    def open_criteria_settings_dialog(self):
        settings = database.get_settings()

        win = tk.Toplevel(self.root)
        win.title("Change Total Marks & Grading Criteria")
        win.geometry("520x460")
        win.resizable(False, False)
        win.grab_set()

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Configure Result Calculation & Output Criteria", font=("Segoe UI", 12, "bold"), foreground="#1E293B").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # 1. Total Marks Output Mode
        ttk.Label(frame, text="Total Output Format:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        combo_mode = ttk.Combobox(
            frame,
            values=[
                "STANDARD - Total Marks & Percentage",
                "CGPA_10 - 10.0 Point Scale",
                "GPA_4 - 4.0 Point Scale",
                "PERCENTAGE_ONLY - Percentage & Grade",
                "TOTAL_ONLY - Raw Marks Sum"
            ],
            state="readonly",
            width=35
        )

        curr_mode = settings.get("output_mode", "STANDARD")
        mode_mapping = {
            "STANDARD": 0,
            "CGPA_10": 1,
            "GPA_4": 2,
            "PERCENTAGE_ONLY": 3,
            "TOTAL_ONLY": 4
        }
        combo_mode.current(mode_mapping.get(curr_mode, 0))
        combo_mode.grid(row=1, column=1, sticky="w", pady=6)

        # 2. Passing Percentage Threshold
        ttk.Label(frame, text="Minimum Passing %:").grid(row=2, column=0, sticky="w", pady=6)
        entry_pass_pct = ttk.Spinbox(frame, from_=25, to=60, width=10)
        entry_pass_pct.set(int(settings.get("pass_percentage", 35)))
        entry_pass_pct.grid(row=2, column=1, sticky="w", pady=6)

        # 3. Individual Subject Pass Requirement
        var_indiv = tk.IntVar(value=settings.get("individual_pass_required", 1))
        chk_indiv = ttk.Checkbutton(frame, text="Student must pass every individual subject", variable=var_indiv)
        chk_indiv.grid(row=3, column=0, columnspan=2, sticky="w", pady=6)

        # 4. Grade Thresholds
        ttk.Separator(frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(frame, text="Grade Thresholds (%):", font=("Segoe UI", 10, "bold")).grid(row=5, column=0, sticky="w", pady=4)

        grades_frame = ttk.Frame(frame)
        grades_frame.grid(row=6, column=0, columnspan=2, sticky="w", pady=4)

        ttk.Label(grades_frame, text="A+ ≥").grid(row=0, column=0, padx=2)
        ent_aplus = ttk.Entry(grades_frame, width=5)
        ent_aplus.insert(0, str(int(settings.get("grade_aplus", 90))))
        ent_aplus.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(grades_frame, text="A ≥").grid(row=0, column=2, padx=2)
        ent_a = ttk.Entry(grades_frame, width=5)
        ent_a.insert(0, str(int(settings.get("grade_a", 80))))
        ent_a.grid(row=0, column=3, padx=(0, 10))

        ttk.Label(grades_frame, text="B ≥").grid(row=0, column=4, padx=2)
        ent_b = ttk.Entry(grades_frame, width=5)
        ent_b.insert(0, str(int(settings.get("grade_b", 70))))
        ent_b.grid(row=0, column=5, padx=(0, 10))

        ttk.Label(grades_frame, text="C ≥").grid(row=0, column=6, padx=2)
        ent_c = ttk.Entry(grades_frame, width=5)
        ent_c.insert(0, str(int(settings.get("grade_c", 60))))
        ent_c.grid(row=0, column=7, padx=(0, 10))

        ttk.Label(grades_frame, text="D ≥").grid(row=0, column=8, padx=2)
        ent_d = ttk.Entry(grades_frame, width=5)
        ent_d.insert(0, str(int(settings.get("grade_d", 50))))
        ent_d.grid(row=0, column=9)

        def save_and_recalculate(recalculate=True):
            mode_choice = combo_mode.get().split(" - ")[0].strip()
            try:
                pass_p = float(entry_pass_pct.get())
                ap = float(ent_aplus.get())
                a = float(ent_a.get())
                b = float(ent_b.get())
                c = float(ent_c.get())
                d = float(ent_d.get())
            except ValueError:
                messagebox.showerror("Error", "All criteria thresholds must be valid numbers.", parent=win)
                return

            new_settings = {
                "output_mode": mode_choice,
                "pass_percentage": pass_p,
                "individual_pass_required": var_indiv.get(),
                "grade_aplus": ap,
                "grade_a": a,
                "grade_b": b,
                "grade_c": c,
                "grade_d": d
            }

            database.update_settings(new_settings)

            if recalculate:
                count = database.recalculate_all_with_new_criteria()
                messagebox.showinfo("Criteria Applied", f"Criteria updated and {count} student records recalculated!", parent=win)
            else:
                messagebox.showinfo("Saved", "Settings saved successfully for new entries.", parent=win)

            win.destroy()
            self.load_all_records()

        # Action Buttons
        btn_action_frame = ttk.Frame(frame)
        btn_action_frame.grid(row=7, column=0, columnspan=2, pady=25)

        btn_recalc = ttk.Button(
            btn_action_frame,
            text="🔄 Apply & Recalculate All Existing Results",
            style="Accent.TButton",
            command=lambda: save_and_recalculate(True)
        )
        btn_recalc.pack(side="left", padx=5)

    # ---------------- MARKSHEET MODAL ----------------
    def open_marksheet_modal(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Student", "Please select a student from the table to generate their Marksheet.")
            return

        roll_no = self.tree.item(selected[0])["values"][0]
        student = database.get_student_by_roll(str(roll_no))
        if not student:
            return

        modal = tk.Toplevel(self.root)
        modal.title(f"Official Marksheet - Roll No {student['roll_no']}")
        modal.geometry("580x680")
        modal.resizable(False, False)
        modal.grab_set()

        card = tk.Frame(modal, bg="white", bd=2, relief="groove")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Title
        tk.Label(card, text="COLLEGE OF ENGINEERING & TECHNOLOGY", font=("Segoe UI", 13, "bold"), bg="white", fg="#1E293B").pack(pady=(15, 2))
        tk.Label(card, text="ACADEMIC TRANSCRIPT & PERFORMANCE REPORT", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").pack()
        tk.Frame(card, bg="#CBD5E1", height=2).pack(fill="x", padx=20, pady=10)

        # Student Details Box
        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(fill="x", padx=30, pady=5)

        tk.Label(info_frame, text=f"Roll Number:  {student['roll_no']}", font=("Segoe UI", 10, "bold"), bg="white", anchor="w").grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text=f"Date:  {datetime.now().strftime('%d-%b-%Y')}", font=("Segoe UI", 9), bg="white", anchor="e").grid(row=0, column=1, sticky="e", pady=2)

        tk.Label(info_frame, text=f"Student Name: {student['name']}", font=("Segoe UI", 10), bg="white", anchor="w").grid(row=1, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text=f"Class/Sem:    {student['class_name']}", font=("Segoe UI", 10), bg="white", anchor="w").grid(row=2, column=0, sticky="w", pady=2)

        # Subject Marks Table
        tk.Frame(card, bg="#E2E8F0", height=1).pack(fill="x", padx=25, pady=8)

        table_frame = tk.Frame(card, bg="white")
        table_frame.pack(fill="x", padx=30, pady=5)

        headers = ["Subject", "Max Marks", "Passing", "Marks Obtained"]
        for col_idx, h in enumerate(headers):
            tk.Label(table_frame, text=h, font=("Segoe UI", 9, "bold"), bg="#F1F5F9", relief="flat", padx=5, pady=4).grid(row=0, column=col_idx, sticky="ew")

        subjects_catalog = {s["name"]: s for s in database.get_subjects()}
        row_counter = 1
        for sub_name, marks in student["marks"].items():
            sub_meta = subjects_catalog.get(sub_name, {"max_marks": 100, "pass_marks": 35})
            is_passed = marks >= sub_meta["pass_marks"]

            tk.Label(table_frame, text=sub_name, font=("Segoe UI", 9), bg="white", anchor="w").grid(row=row_counter, column=0, sticky="w", pady=3)
            tk.Label(table_frame, text=str(sub_meta["max_marks"]), font=("Segoe UI", 9), bg="white").grid(row=row_counter, column=1, pady=3)
            tk.Label(table_frame, text=str(sub_meta["pass_marks"]), font=("Segoe UI", 9), bg="white").grid(row=row_counter, column=2, pady=3)
            tk.Label(
                table_frame, text=str(marks), font=("Segoe UI", 9, "bold"), bg="white",
                fg="#059669" if is_passed else "#DC2626"
            ).grid(row=row_counter, column=3, pady=3)

            row_counter += 1

        table_frame.grid_columnconfigure(0, weight=2)
        table_frame.grid_columnconfigure(1, weight=1)
        table_frame.grid_columnconfigure(2, weight=1)
        table_frame.grid_columnconfigure(3, weight=1)

        tk.Frame(card, bg="#CBD5E1", height=2).pack(fill="x", padx=25, pady=10)

        # Summary Footers
        summary_frame = tk.Frame(card, bg="white")
        summary_frame.pack(fill="x", padx=30, pady=5)

        tk.Label(summary_frame, text=f"Total Output Criteria:  {student['criteria_output']}", font=("Segoe UI", 11, "bold"), bg="white", fg="#2563EB").pack(anchor="w", pady=2)
        tk.Label(summary_frame, text=f"Percentage:             {student['percentage']:.2f}%", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=2)
        tk.Label(summary_frame, text=f"Final Grade:            {student['grade']}", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=2)

        res_color = "#059669" if student["status"] == "PASS" else "#DC2626"
        tk.Label(summary_frame, text=f"Result Status:          {student['status']}", font=("Segoe UI", 12, "bold"), bg="white", fg=res_color).pack(anchor="w", pady=4)

        # Save to File / Print Button
        def export_txt():
            out_name = f"Marksheet_{student['roll_no']}.txt"
            content = f"""====================================================
      COLLEGE OF ENGINEERING & TECHNOLOGY
        ACADEMIC MARKSHEET TRANSCRIPT
====================================================
Roll Number : {student['roll_no']}
Student Name: {student['name']}
Class/Sem   : {student['class_name']}
Gender      : {student['gender']}
Date        : {datetime.now().strftime('%d-%b-%Y')}
----------------------------------------------------
Subject                        Max   Pass   Obtained
----------------------------------------------------
"""
            for sub_name, marks in student["marks"].items():
                meta = subjects_catalog.get(sub_name, {"max_marks": 100, "pass_marks": 35})
                content += f"{sub_name:<30} {meta['max_marks']:<6} {meta['pass_marks']:<6} {marks}\n"

            content += f"""----------------------------------------------------
Output Criteria : {student['criteria_output']}
Percentage      : {student['percentage']:.2f}%
Grade           : {student['grade']}
Result Status   : {student['status']}
====================================================
Authorized Signatory: _________________________
"""
            filepath = os.path.join("d:\\Personal\\krishna python project", out_name)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Exported", f"Official Marksheet saved to:\n{filepath}", parent=modal)

        btn_export = ttk.Button(card, text="💾 Save / Export Marksheet as Text File", style="Accent.TButton", command=export_txt)
        btn_export.pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentResultApp(root)
    root.mainloop()
