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

### Setup on Windows PowerShell
1. Install and start MySQL Server 8.0. The setup script creates the database, so the configured MySQL user must have permission to create databases.
2. Clone the project and enter its folder:
```powershell
git clone https://github.com/goswamibhasker3-oss/student-management-system.git
cd student-management-system
```
3. Create and activate a virtual environment, then install dependencies:
```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in that terminal, then activate again.

4. Create `.env` from the example if it does not already exist, then set your local MySQL credentials:
```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```
5. Initialize the database and create your admin account. The password is entered privately in the terminal and must be at least 12 characters:
```powershell
python seed.py
```
6. Start the app:
```powershell
python app.py
```
Open <http://127.0.0.1:5000> and sign in with the admin username and password you created.