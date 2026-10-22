import sqlite3
import json

DB_NAME = "results.db"

DEFAULT_SETTINGS = {
    "output_mode": "STANDARD",            # STANDARD, CGPA_10, GPA_4, PERCENTAGE_ONLY, TOTAL_ONLY
    "pass_percentage": 35.0,
    "individual_pass_required": 1,         # 1 = True, 0 = False
    "grade_aplus": 90.0,
    "grade_a": 80.0,
    "grade_b": 70.0,
    "grade_c": 60.0,
    "grade_d": 50.0
}

DEFAULT_SUBJECTS = [
    ("Python Programming", 100, 35),
    ("Data Structures (DSA)", 100, 35),
    ("Database Systems (DBMS)", 100, 35),
    ("Computer Networks (CN)", 100, 35),
    ("Operating Systems (OS)", 100, 35)
]

def get_connection():
    """Returns a connection to the SQLite database with row factory."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_settings():
    """Fetches all system criteria and settings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()

    settings = dict(DEFAULT_SETTINGS)
    for r in rows:
        key = r["key"]
        val = r["value"]
        if key in ["pass_percentage", "grade_aplus", "grade_a", "grade_b", "grade_c", "grade_d"]:
            settings[key] = float(val)
        elif key in ["individual_pass_required"]:
            settings[key] = int(val)
        else:
            settings[key] = val
    return settings

def update_settings(new_settings):
    """Updates settings in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    for k, v in new_settings.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
    conn.commit()
    conn.close()

def get_subjects():
    """Returns list of all subjects [ {'name': ..., 'max_marks': ..., 'pass_marks': ...} ]."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, max_marks, pass_marks FROM subjects ORDER BY rowid ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_subject(name, max_marks=100, pass_marks=35):
    """Adds a new subject to the subject catalog."""
    name = name.strip()
    if not name:
        return False, "Subject name cannot be empty."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO subjects (name, max_marks, pass_marks) VALUES (?, ?, ?)",
            (name, int(max_marks), int(pass_marks))
        )
        conn.commit()
        conn.close()
        return True, f"Subject '{name}' added successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"Subject '{name}' already exists!"

def delete_subject(name):
    """Deletes a subject from the catalog."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return True, f"Subject '{name}' removed."

def calculate_result(marks_dict, settings=None):
    """
    Calculates total marks, max marks, percentage, grade, status, and formatted criteria output.
    marks_dict format: { "Subject Name": marks_obtained, ... }
    """
    if settings is None:
        settings = get_settings()

    subjects_info = {s["name"]: s for s in get_subjects()}

    total_obtained = 0
    total_max = 0
    failed_individual = False

    for sub_name, marks in marks_dict.items():
        total_obtained += marks
        sub_info = subjects_info.get(sub_name, {"max_marks": 100, "pass_marks": 35})
        total_max += sub_info["max_marks"]

        if settings.get("individual_pass_required", 1) and marks < sub_info["pass_marks"]:
            failed_individual = True

    if total_max > 0:
        percentage = round((total_obtained / float(total_max)) * 100.0, 2)
    else:
        percentage = 0.0

    # Determine Pass / Fail
    min_pass_pct = settings.get("pass_percentage", 35.0)
    if failed_individual or percentage < min_pass_pct:
        status = "FAIL"
        grade = "F"
    else:
        status = "PASS"
        if percentage >= settings.get("grade_aplus", 90.0):
            grade = "A+"
        elif percentage >= settings.get("grade_a", 80.0):
            grade = "A"
        elif percentage >= settings.get("grade_b", 70.0):
            grade = "B"
        elif percentage >= settings.get("grade_c", 60.0):
            grade = "C"
        elif percentage >= settings.get("grade_d", 50.0):
            grade = "D"
        else:
            grade = "E"

    # Formatted Criteria Output
    mode = settings.get("output_mode", "STANDARD")
    if mode == "CGPA_10":
        # 10 Point CGPA scale: (Percentage / 9.5) or (Percentage / 10.0)
        cgpa = round(min(10.0, percentage / 9.5), 2)
        criteria_output = f"CGPA: {cgpa:.2f} / 10.0"
    elif mode == "GPA_4":
        # 4 Point US GPA scale
        gpa = round(min(4.0, (percentage / 100.0) * 4.0), 2)
        criteria_output = f"GPA: {gpa:.2f} / 4.0"
    elif mode == "PERCENTAGE_ONLY":
        criteria_output = f"{percentage:.1f}% ({grade})"
    elif mode == "TOTAL_ONLY":
        criteria_output = f"{total_obtained} / {total_max}"
    else:
        # STANDARD: Total + Percentage
        criteria_output = f"{total_obtained}/{total_max} ({percentage:.1f}%)"

    return total_obtained, total_max, percentage, grade, status, criteria_output

def initialize_database():
    """Creates tables and populates defaults."""
    conn = get_connection()
    cursor = conn.cursor()

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    # Seed default settings
    for k, v in DEFAULT_SETTINGS.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))

    # Subjects catalog table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        name TEXT PRIMARY KEY,
        max_marks INTEGER NOT NULL DEFAULT 100,
        pass_marks INTEGER NOT NULL DEFAULT 35
    )
    """)

    # Seed default subjects if empty
    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO subjects (name, max_marks, pass_marks) VALUES (?, ?, ?)", DEFAULT_SUBJECTS)

    # Student Results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_results (
        roll_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        class_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        marks_json TEXT NOT NULL,
        total INTEGER NOT NULL,
        max_total INTEGER NOT NULL,
        percentage REAL NOT NULL,
        grade TEXT NOT NULL,
        status TEXT NOT NULL,
        criteria_output TEXT NOT NULL
    )
    """)

    # Commit schema creation before seeding
    conn.commit()

    # Seed initial students if empty
    cursor.execute("SELECT COUNT(*) FROM student_results")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ("101", "Aarav Sharma", "B.Tech Sem 5", "Male", {"Python Programming": 92, "Data Structures (DSA)": 88, "Database Systems (DBMS)": 95, "Computer Networks (CN)": 90, "Operating Systems (OS)": 89}),
            ("102", "Priya Patel", "B.Tech Sem 5", "Female", {"Python Programming": 85, "Data Structures (DSA)": 78, "Database Systems (DBMS)": 82, "Computer Networks (CN)": 88, "Operating Systems (OS)": 80}),
            ("103", "Rahul Verma", "B.Tech Sem 5", "Male", {"Python Programming": 65, "Data Structures (DSA)": 70, "Database Systems (DBMS)": 58, "Computer Networks (CN)": 62, "Operating Systems (OS)": 60}),
            ("104", "Ananya Iyer", "B.Tech Sem 5", "Female", {"Python Programming": 95, "Data Structures (DSA)": 92, "Database Systems (DBMS)": 94, "Computer Networks (CN)": 98, "Operating Systems (OS)": 91}),
            ("105", "Dev Dave", "B.Tech Sem 5", "Male", {"Python Programming": 32, "Data Structures (DSA)": 55, "Database Systems (DBMS)": 60, "Computer Networks (CN)": 48, "Operating Systems (OS)": 52})
        ]

        curr_settings = dict(DEFAULT_SETTINGS)
        for s in sample_students:
            roll, name, c_name, gender, marks_dict = s
            tot, max_tot, pct, grade, status, crit_out = calculate_result(marks_dict, curr_settings)
            cursor.execute("""
                INSERT INTO student_results 
                (roll_no, name, class_name, gender, marks_json, total, max_total, percentage, grade, status, criteria_output)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (roll, name, c_name, gender, json.dumps(marks_dict), tot, max_tot, pct, grade, status, crit_out))

    conn.commit()
    conn.close()

# ---------------- CRUD Operations ----------------

def add_student_result(roll_no, name, class_name, gender, marks_dict):
    """Adds a new student result."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT roll_no FROM student_results WHERE roll_no = ?", (roll_no.strip(),))
    if cursor.fetchone():
        conn.close()
        return False, f"Roll Number '{roll_no}' already exists! Use Update instead."

    settings = get_settings()
    tot, max_tot, pct, grade, status, crit_out = calculate_result(marks_dict, settings)

    cursor.execute("""
        INSERT INTO student_results 
        (roll_no, name, class_name, gender, marks_json, total, max_total, percentage, grade, status, criteria_output)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (roll_no.strip(), name.strip(), class_name.strip(), gender, json.dumps(marks_dict), tot, max_tot, pct, grade, status, crit_out))

    conn.commit()
    conn.close()
    return True, f"Result for '{name}' (Roll No: {roll_no}) saved successfully!"

def update_student_result(roll_no, name, class_name, gender, marks_dict):
    """Updates an existing student result."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT roll_no FROM student_results WHERE roll_no = ?", (roll_no.strip(),))
    if not cursor.fetchone():
        conn.close()
        return False, f"Student with Roll No '{roll_no}' not found."

    settings = get_settings()
    tot, max_tot, pct, grade, status, crit_out = calculate_result(marks_dict, settings)

    cursor.execute("""
        UPDATE student_results
        SET name = ?, class_name = ?, gender = ?, marks_json = ?,
            total = ?, max_total = ?, percentage = ?, grade = ?, status = ?, criteria_output = ?
        WHERE roll_no = ?
    """, (name.strip(), class_name.strip(), gender, json.dumps(marks_dict), tot, max_tot, pct, grade, status, crit_out, roll_no.strip()))

    conn.commit()
    conn.close()
    return True, f"Record for Roll No '{roll_no}' updated successfully!"

def delete_student_result(roll_no):
    """Deletes a student record."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM student_results WHERE roll_no = ?", (roll_no.strip(),))
    record = cursor.fetchone()
    if not record:
        conn.close()
        return False, f"Roll No '{roll_no}' does not exist."

    student_name = record["name"]
    cursor.execute("DELETE FROM student_results WHERE roll_no = ?", (roll_no.strip(),))
    conn.commit()
    conn.close()
    return True, f"Record for '{student_name}' (Roll: {roll_no}) deleted successfully."

def get_all_results():
    """Retrieves all student results."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_results ORDER BY roll_no ASC")
    rows = cursor.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        d["marks"] = json.loads(d["marks_json"])
        res.append(d)
    return res

def search_results(query):
    """Searches students by roll number or name."""
    conn = get_connection()
    cursor = conn.cursor()
    search_term = f"%{query.strip()}%"
    cursor.execute("""
        SELECT * FROM student_results 
        WHERE roll_no LIKE ? OR name LIKE ?
        ORDER BY roll_no ASC
    """, (search_term, search_term))
    rows = cursor.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        d["marks"] = json.loads(d["marks_json"])
        res.append(d)
    return res

def get_student_by_roll(roll_no):
    """Fetches a single student result dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_results WHERE roll_no = ?", (roll_no.strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["marks"] = json.loads(d["marks_json"])
    return d

def recalculate_all_with_new_criteria():
    """Recomputes total, percentage, grade, and criteria output for all students based on updated settings."""
    settings = get_settings()
    students = get_all_results()

    conn = get_connection()
    cursor = conn.cursor()
    for s in students:
        tot, max_tot, pct, grade, status, crit_out = calculate_result(s["marks"], settings)
        cursor.execute("""
            UPDATE student_results
            SET total = ?, max_total = ?, percentage = ?, grade = ?, status = ?, criteria_output = ?
            WHERE roll_no = ?
        """, (tot, max_tot, pct, grade, status, crit_out, s["roll_no"]))

    conn.commit()
    conn.close()
    return len(students)
