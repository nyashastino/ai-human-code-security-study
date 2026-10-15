# SAMPLE_11_CRUD_PYTHON
import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "student_records_app"),
}


def get_connection(include_database=True):
    config = dict(DB_CONFIG)
    if not include_database:
        config.pop("database", None)
    return mysql.connector.connect(**config)


def init_db():
    conn = get_connection(include_database=False)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
    conn.commit()
    cursor.close()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INT NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            course VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def ensure_templates():
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    os.makedirs(template_dir, exist_ok=True)

    layout_html = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{{ title or 'Students' }}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f5f5f5; }
    .actions { display: flex; gap: 8px; }
    .btn { padding: 8px 12px; border: 1px solid #444; background: #fff; cursor: pointer; text-decoration: none; color: #111; }
    .btn-primary { background: #111; color: #fff; }
    form.inline { display: inline; }
    .container { max-width: 1000px; margin: 0 auto; }
    .error { color: #b00020; margin-bottom: 12px; }
    .field { margin-bottom: 12px; }
    label { display: block; margin-bottom: 6px; }
    input { width: 100%; padding: 8px; box-sizing: border-box; }
  </style>
</head>
<body>
  <div class=\"container\">{% block content %}{% endblock %}</div>
</body>
</html>
"""

    students_html = """{% extends 'layout.html' %}
{% block content %}
  <h1>Students</h1>
  <p><a class=\"btn btn-primary\" href=\"{{ url_for('add_student_form') }}\">Add Student</a></p>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Age</th>
        <th>Email</th>
        <th>Course</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for student in students %}
      <tr>
        <td>{{ student.id }}</td>
        <td>{{ student.name }}</td>
        <td>{{ student.age }}</td>
        <td>{{ student.email }}</td>
        <td>{{ student.course }}</td>
        <td>
          <div class=\"actions\">
            <a class=\"btn\" href=\"{{ url_for('edit_student_form', student_id=student.id) }}\">Edit</a>
            <form class=\"inline\" method=\"post\" action=\"{{ url_for('delete_student', student_id=student.id) }}\">
              <button class=\"btn\" type=\"submit\">Delete</button>
            </form>
          </div>
        </td>
      </tr>
      {% endfor %}
      {% if not students %}
      <tr><td colspan=\"6\">No records found.</td></tr>
      {% endif %}
    </tbody>
  </table>
{% endblock %}
"""

    form_html = """{% extends 'layout.html' %}
{% block content %}
  <h1>{{ heading }}</h1>
  {% if error %}<div class=\"error\">{{ error }}</div>{% endif %}
  <form method=\"post\" action=\"{{ action_url }}\">
    <div class=\"field\">
      <label for=\"name\">Name</label>
      <input id=\"name\" name=\"name\" type=\"text\" value=\"{{ student.name if student else '' }}\" required>
    </div>
    <div class=\"field\">
      <label for=\"age\">Age</label>
      <input id=\"age\" name=\"age\" type=\"number\" min=\"0\" value=\"{{ student.age if student else '' }}\" required>
    </div>
    <div class=\"field\">
      <label for=\"email\">Email</label>
      <input id=\"email\" name=\"email\" type=\"email\" value=\"{{ student.email if student else '' }}\" required>
    </div>
    <div class=\"field\">
      <label for=\"course\">Course</label>
      <input id=\"course\" name=\"course\" type=\"text\" value=\"{{ student.course if student else '' }}\" required>
    </div>
    <button class=\"btn btn-primary\" type=\"submit\">{{ submit_label }}</button>
    <a class=\"btn\" href=\"{{ url_for('list_students') }}\">Cancel</a>
  </form>
{% endblock %}
"""

    with open(os.path.join(template_dir, "layout.html"), "w", encoding="utf-8") as f:
        f.write(layout_html)
    with open(os.path.join(template_dir, "students.html"), "w", encoding="utf-8") as f:
        f.write(students_html)
    with open(os.path.join(template_dir, "student_form.html"), "w", encoding="utf-8") as f:
        f.write(form_html)


def validate_input(form_data):
    name = form_data.get("name", "").strip()
    age_raw = form_data.get("age", "").strip()
    email = form_data.get("email", "").strip()
    course = form_data.get("course", "").strip()

    if not name or not age_raw or not email or not course:
        return None, "All fields are required"

    try:
        age = int(age_raw)
        if age < 0:
            raise ValueError()
    except ValueError:
        return None, "Age must be a non-negative integer"

    return {"name": name, "age": age, "email": email, "course": course}, None


def get_student_by_id(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, age, email, course FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return student


@app.route("/")
def index():
    return redirect(url_for("list_students"))


@app.route("/students")
def list_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, age, email, course FROM students ORDER BY id ASC")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("students.html", title="Students", students=students)


@app.route("/students/add", methods=["GET"])
def add_student_form():
    return render_template(
        "student_form.html",
        title="Add Student",
        heading="Add Student",
        action_url=url_for("add_student"),
        submit_label="Create",
        student=None,
        error=None,
    )


@app.route("/students/add", methods=["POST"])
def add_student():
    payload, error = validate_input(request.form)
    if error:
        return render_template(
            "student_form.html",
            title="Add Student",
            heading="Add Student",
            action_url=url_for("add_student"),
            submit_label="Create",
            student=request.form,
            error=error,
        )

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (name, age, email, course) VALUES (%s, %s, %s, %s)",
            (payload["name"], payload["age"], payload["email"], payload["course"]),
        )
        conn.commit()
    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        return render_template(
            "student_form.html",
            title="Add Student",
            heading="Add Student",
            action_url=url_for("add_student"),
            submit_label="Create",
            student=request.form,
            error="Email already exists",
        )

    cursor.close()
    conn.close()
    return redirect(url_for("list_students"))


@app.route("/students/edit/<int:student_id>", methods=["GET"])
def edit_student_form(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return redirect(url_for("list_students"))

    return render_template(
        "student_form.html",
        title="Edit Student",
        heading="Edit Student",
        action_url=url_for("edit_student", student_id=student_id),
        submit_label="Update",
        student=student,
        error=None,
    )


@app.route("/students/edit/<int:student_id>", methods=["POST"])
def edit_student(student_id):
    existing = get_student_by_id(student_id)
    if not existing:
        return redirect(url_for("list_students"))

    payload, error = validate_input(request.form)
    if error:
        form_student = {
            "id": student_id,
            "name": request.form.get("name", ""),
            "age": request.form.get("age", ""),
            "email": request.form.get("email", ""),
            "course": request.form.get("course", ""),
        }
        return render_template(
            "student_form.html",
            title="Edit Student",
            heading="Edit Student",
            action_url=url_for("edit_student", student_id=student_id),
            submit_label="Update",
            student=form_student,
            error=error,
        )

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE students SET name = %s, age = %s, email = %s, course = %s WHERE id = %s",
            (payload["name"], payload["age"], payload["email"], payload["course"], student_id),
        )
        conn.commit()
    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        form_student = {
            "id": student_id,
            "name": payload["name"],
            "age": payload["age"],
            "email": payload["email"],
            "course": payload["course"],
        }
        return render_template(
            "student_form.html",
            title="Edit Student",
            heading="Edit Student",
            action_url=url_for("edit_student", student_id=student_id),
            submit_label="Update",
            student=form_student,
            error="Email already exists",
        )

    cursor.close()
    conn.close()
    return redirect(url_for("list_students"))


@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("list_students"))


if __name__ == "__main__":
    ensure_templates()
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
