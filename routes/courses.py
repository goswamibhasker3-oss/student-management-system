# routes/courses.py
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

from models import mysql

courses_bp = Blueprint("courses", __name__)


def _get_connection():
    connection = mysql.connection
    if connection is None:
        raise RuntimeError("MySQL connection is unavailable.")
    return connection


# ---------- WTForms ----------
class CourseForm(FlaskForm):
    code = StringField("Course Code", validators=[DataRequired(), Length(max=20)])
    name = StringField("Course Name", validators=[DataRequired(), Length(max=150)])
    credits = IntegerField(
        "Credits",
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        default=3,
    )
    description = TextAreaField(
        "Description", validators=[Optional(), Length(max=1000)]
    )
    submit = SubmitField("Save Course")


# ---------- List ----------
@courses_bp.route("/")
@login_required
def index():
    cur = _get_connection().cursor()
    cur.execute(
        """
        SELECT c.id, c.code, c.name, c.credits, c.description, c.created_at,
               COUNT(s.id) AS student_count
        FROM courses c
        LEFT JOIN students s ON s.course_id = c.id
        GROUP BY c.id
        ORDER BY c.name
        """
    )
    courses = cur.fetchall()
    cur.close()
    return render_template("courses/index.html", courses=courses)


# ---------- Create ----------
@courses_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = CourseForm()
    if form.validate_on_submit():
        cur = _get_connection().cursor()
        try:
            cur.execute(
                "INSERT INTO courses (code, name, credits, description) VALUES (%s, %s, %s, %s)",
                (
                    (form.code.data or "").strip().upper(),
                    (form.name.data or "").strip(),
                    form.credits.data,
                    form.description.data.strip() if form.description.data else None,
                ),
            )
            _get_connection().commit()
            flash("Course created successfully.", "success")
            return redirect(url_for("courses.index"))
        except Exception as e:
            _get_connection().rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cur.close()

    return render_template(
        "courses/form.html", form=form, mode="create", course=None
    )


# ---------- Edit ----------
@courses_bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
def edit(course_id):
    cur = _get_connection().cursor()
    cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cur.fetchone()
    cur.close()

    if not course:
        abort(404)

    form = CourseForm(data=course)
    if form.validate_on_submit():
        cur = _get_connection().cursor()
        try:
            cur.execute(
                "UPDATE courses SET code=%s, name=%s, credits=%s, description=%s WHERE id=%s",
                (
                    (form.code.data or "").strip().upper(),
                    (form.name.data or "").strip(),
                    form.credits.data,
                    form.description.data.strip() if form.description.data else None,
                    course_id,
                ),
            )
            _get_connection().commit()
            flash("Course updated successfully.", "success")
            return redirect(url_for("courses.index"))
        except Exception as e:
            _get_connection().rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cur.close()

    return render_template(
        "courses/form.html", form=form, mode="edit", course=course
    )


# ---------- Delete ----------
@courses_bp.route("/<int:course_id>/delete", methods=["POST"])
@login_required
def delete(course_id):
    cur = _get_connection().cursor()
    cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
    _get_connection().commit()
    cur.close()

    flash("Course deleted.", "info")
    return redirect(url_for("courses.index"))