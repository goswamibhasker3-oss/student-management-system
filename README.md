# 🎓 Student Management System

A full‑stack web application for managing students, courses, and enrollments.
Built as a portfolio project by **Bhaskar Goswami** (B.Sc. Information Technology).

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)

## ✨ Features
- Authentication (login/logout, hashed passwords, session-based, protected routes)
- Dashboard (total students, total courses, active students, recent registrations)
- Student CRUD, search, filter (status + course), pagination
- Course CRUD with enrolled student counts
- Responsive UI (mobile sidebar, cards, tables)

## 🛠 Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python 3, Flask
- **Database:** MySQL 8, SQL
- **Auth:** Flask‑Login + Werkzeug password hashing

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- MySQL 8.0+

### 1. Clone & setup
```bash
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt