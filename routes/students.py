# routes/students.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length

from models import mysql

students_bp = Blueprint("students", __name__)


def _get_connection():
    connection = mysql.connection
    if connection is None:
        raise RuntimeError("MySQL connection is unavailable.")
    return connection


# ---------- WTForms ----------
class StudentForm(FlaskForm):
    roll_no = StringField("Roll No", validators=[DataRequired(), Length(max=30)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=60)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=60)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    gender = SelectField(
        "Gender",
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
    )
    dob = DateField("Date of Birth", validators=[Optional()], format="%Y-%m-%d")
    address = TextAreaField("Address", validators=[Optional(), Length(max=255)])
    course_id = SelectField("Course", coerce=int)
    status = SelectField(
        "Status",
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("graduated", "Graduated"),
        ],
    )
    submit = SubmitField("Save Student")

    def load_courses(self):
        cur = _get_connection().cursor()
        cur.execute("SELECT id, code, name FROM courses ORDER BY name")
        rows = cur.fetchall()
        cur.close()
        self.course_id.choices = [(0, "— Not assigned —")] + [
            (r["id"], f"{r['code']} · {r['name']}") for r in rows
        ]


# ---------- Helper ----------
def _get_courses():
    cur = _get_connection().cursor()
    cur.execute("SELECT id, code, name FROM courses ORDER BY name")
    rows = cur.fetchall()
    cur.close()
    return rows


# ---------- List + Search + Filter + Pagination ----------
@students_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    course_id = request.args.get("course_id", type=int)
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = 8

    where, params = [], []
    if q:
        where.append(
            "(s.first_name LIKE %s OR s.last_name LIKE %s OR s.roll_no LIKE %s OR s.email LIKE %s)"
        )
        like = f"%{q}%"
        params.extend([like, like, like, like])
    if status in ("active", "inactive", "graduated"):
        where.append("s.status = %s")
        params.append(status)
    if course_id:
        where.append("s.course_id = %s")
        params.append(course_id)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    cur = _get_connection().cursor()

    cur.execute(f"SELECT COUNT(*) AS c FROM students s {where_sql}", params)
    total = cur.fetchone()["c"]

    cur.execute(
        f"""
        SELECT s.id, s.roll_no, s.first_name, s.last_name, s.email,
               s.phone, s.status, s.created_at,
               c.name AS course_name, c.code AS course_code
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        {where_sql}
        ORDER BY s.created_at DESC
        LIMIT %s OFFSET %s
        """,
        params + [per_page, (page - 1) * per_page],
    )
    students = cur.fetchall()
    cur.close()

    total_pages = max((total + per_page - 1) // per_page, 1)

    return render_template(
        "students/index.html",
        students=students,
        courses=_get_courses(),
        q=q,
        status=status,
        course_id=course_id or 0,
        page=page,
        total_pages=total_pages,
        total=total,
    )


# ---------- Create ----------
@students_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = StudentForm()
    form.load_courses()

    if form.validate_on_submit():
        cur = _get_connection().cursor()
        try:
            cur.execute(
                """INSERT INTO students
                   (roll_no, first_name, last_name, email, phone, gender, dob,
                    address, course_id, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    (form.roll_no.data or "").strip(),
                    (form.first_name.data or "").strip(),
                    (form.last_name.data or "").strip(),
                    (form.email.data or "").strip().lower(),
                    form.phone.data.strip() if form.phone.data else None,
                    form.gender.data,
                    form.dob.data,
                    form.address.data.strip() if form.address.data else None,
                    form.course_id.data or None,
                    form.status.data,
                ),
            )
            _get_connection().commit()
            flash("Student added successfully.", "success")
            return redirect(url_for("students.index"))
        except Exception as e:
            _get_connection().rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cur.close()

    return render_template(
        "students/form.html", form=form, mode="create", student=None
    )


# ---------- View ----------
@students_bp.route("/<int:student_id>")
@login_required
def view(student_id):
    cur = _get_connection().cursor()
    cur.execute(
        """
        SELECT s.*, c.name AS course_name, c.code AS course_code
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        WHERE s.id = %s
        """,
        (student_id,),
    )
    student = cur.fetchone()
    cur.close()

    if not student:
        abort(404)

    return render_template("students/view.html", student=student)


# ---------- Edit ----------
@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit(student_id):
    cur = _get_connection().cursor()
    cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()
    cur.close()

    if not student:
        abort(404)

    form = StudentForm(data=student)
    form.load_courses()

    if form.validate_on_submit():
        cur = _get_connection().cursor()
        try:
            cur.execute(
                """UPDATE students SET
                   roll_no=%s, first_name=%s, last_name=%s, email=%s, phone=%s,
                   gender=%s, dob=%s, address=%s, course_id=%s, status=%s
                   WHERE id=%s""",
                (
                    (form.roll_no.data or "").strip(),
                    (form.first_name.data or "").strip(),
                    (form.last_name.data or "").strip(),
                    (form.email.data or "").strip().lower(),
                    form.phone.data.strip() if form.phone.data else None,
                    form.gender.data,
                    form.dob.data,
                    form.address.data.strip() if form.address.data else None,
                    form.course_id.data or None,
                    form.status.data,
                    student_id,
                ),
            )
            _get_connection().commit()
            flash("Student updated successfully.", "success")
            return redirect(url_for("students.view", student_id=student_id))
        except Exception as e:
            _get_connection().rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cur.close()

    return render_template(
        "students/form.html", form=form, mode="edit", student=student
    )


# ---------- Delete ----------
@students_bp.route("/<int:student_id>/delete", methods=["POST"])
@login_required
def delete(student_id):
    cur = _get_connection().cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
    _get_connection().commit()
    cur.close()

    flash("Student deleted.", "info")
    return redirect(url_for("students.index"))