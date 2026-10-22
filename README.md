# Student Result Management System

A simple, robust desktop application developed using **Pure Python** and **SQLite** for managing student grades, calculating customizable output criteria (Percentages, CGPA, US GPA), adding dynamic subjects, and generating official student marksheet cards.

---

## 📌 Project Overview
The **Student Result Management System** simplifies the record-keeping and grade evaluation process for educational institutions. Teachers can register students, dynamically add/delete subjects, configure custom criteria for how total marks are outputted (Percentage, CGPA, GPA), and generate printable marksheets.

---

## ✨ Key Features

1. **➕ Dynamic Subjects ("Add Subject" Button):**
   - Click the **"➕ Add Subject"** button to add new subjects to the system.
   - Configure **Subject Name**, **Maximum Marks** (e.g., 100, 50, 75), and **Passing Marks** (e.g., 35, 20).
   - The student entry form dynamically re-renders to include input fields for all active subjects.
   - Delete/manage existing subjects with one click (`✕`).

2. **⚙️ Customizable Total Marks Output Criteria ("Change Criteria" Option):**
   - Click **"⚙️ Change Total Marks Criteria"** in the header or bottom bar to customize:
     - **Output Format Mode:**
       - **STANDARD:** Total Marks Sum & Percentage (e.g., `450/500 (90.0%)`)
       - **CGPA_10:** 10.0-Point CGPA Scale (e.g., `CGPA: 9.47 / 10.0`)
       - **GPA_4:** 4.0-Point US GPA Scale (e.g., `GPA: 3.60 / 4.0`)
       - **PERCENTAGE_ONLY:** Percentage & Grade (e.g., `90.0% (A+)`)
       - **TOTAL_ONLY:** Raw Marks Sum (e.g., `450 / 500`)
     - **Minimum Passing Percentage:** Set passing threshold (e.g., 35%, 40%, 50%).
     - **Individual Subject Passing Rule:** Toggle whether students must pass each individual subject.
     - **Custom Grade Thresholds:** Adjust cutoffs for $A+, A, B, C, D$.
     - **Instant Recalculation:** Click *"Apply & Recalculate All Existing Results"* to recompute all existing records instantly.

3. **Student Record Management (CRUD):**
   - **Add New Result:** Enter Roll Number, Name, Class, Gender, and subject marks.
   - **Update Record:** Modify student information or update scores.
   - **Delete Record:** Remove records with a confirmation prompt.
   - **Clear Form:** Reset input fields for rapid data entry.

4. **Search & Real-time Filter:**
   - Search records in real-time by Roll Number or Student Name.
   - Click *"Show All"* to reset search filters.

5. **Official Marksheet Card & Export:**
   - Click **"View & Print Student Marksheet Card"** to generate an academic transcript modal.
   - Displays subject breakdowns, maximum vs. obtained marks, passing status, and selected total criteria output.
   - Includes a **"Save / Export Marksheet as Text File"** button to export a `.txt` marksheet.

---

## 🛠️ Technology Stack
* **Language:** Python 3.8+ (Pure Python)
* **GUI Framework:** `tkinter` & `ttk` (Standard native desktop interface)
* **Database:** `sqlite3` (Embedded database: `results.db`)
* **Data Format:** `json` (for dynamic subject-marks mapping)
* **Dependencies:** None! (100% built-in Python standard library, zero `pip install` required)

---

## 📂 Project Structure
```text
krishna python project/
│
├── main.py          # Tkinter GUI (Dynamic Forms, Table, Criteria Modal, Marksheets)
├── database.py      # SQLite schema, dynamic subjects catalog, settings, calculations
├── results.db       # Auto-created SQLite database file
└── README.md        # Documentation and Viva preparation guide
```

---

## 🚀 How to Run the Project

1. Open PowerShell or Command Prompt.
2. Navigate to the project directory:
   ```powershell
   cd "d:\Personal\krishna python project"
   ```
3. Run the application:
   ```powershell
   python main.py
   ```

---

## 💡 Top Viva / Presentation Questions & Answers

**Q1: How are subjects dynamically added without breaking the database table schema?**
> **Answer:** Instead of hardcoding subject column names into the SQL table, subjects are managed in a separate `subjects` catalog table, and student marks are stored as a JSON object (`marks_json`) in SQLite. This allows teachers to add or remove subjects at any time without needing schema migrations.

**Q2: How does the system handle different total marks output criteria?**
> **Answer:** In `database.py`, system criteria settings (`output_mode`, `pass_percentage`, grade cutoffs) are stored in a `settings` table. When the user changes criteria, `calculate_result()` computes the appropriate scale (Standard Total, 10.0 CGPA, 4.0 GPA, or Percentage Only) and formats the output string accordingly.

**Q3: How does the recalculate function work?**
> **Answer:** When criteria are updated, `recalculate_all_with_new_criteria()` fetches all existing student records, re-runs the calculation engine with the new settings, and updates the database records in batch, immediately refreshing the UI table.
