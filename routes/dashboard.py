# routes/dashboard.py
from flask import Blueprint, render_template
from flask_login import login_required

from models import mysql

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    """Show aggregate stats + recent registrations + per-course enrollment."""
    connection = mysql.connection
    if connection is None:
        raise RuntimeError("MySQL connection is unavailable.")
    cur = connection.cursor()

    # Total students
    cur.execute("SELECT COUNT(*) AS c FROM students")
    total_students = cur.fetchone()["c"]

    # Total courses
    cur.execute("SELECT COUNT(*) AS c FROM courses")
    total_courses = cur.fetchone()["c"]

    # Active students
    cur.execute("SELECT COUNT(*) AS c FROM students WHERE status = 'active'")
    active_students = cur.fetchone()["c"]

    # Recent registrations (latest 5)
    cur.execute(
        """
        SELECT s.id, s.roll_no, s.first_name, s.last_name, s.email,
               s.status, s.created_at,
               c.name AS course_name, c.code AS course_code
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        ORDER BY s.created_at DESC
        LIMIT 5
        """
    )
    recent = cur.fetchall()

    # Enrollment per course (top 6)
    cur.execute(
        """
        SELECT c.id, c.code, c.name, COUNT(s.id) AS student_count
        FROM courses c
        LEFT JOIN students s ON s.course_id = c.id
        GROUP BY c.id, c.code, c.name
        ORDER BY student_count DESC
        LIMIT 6
        """
    )
    course_stats = cur.fetchall()

    cur.close()

    # Normalise for the bar chart width
    max_count = max([c["student_count"] for c in course_stats], default=1) or 1

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        active_students=active_students,
        recent=recent,
        course_stats=course_stats,
        max_count=max_count,
    )