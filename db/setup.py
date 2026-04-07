import sqlite3
import os
from datetime import date, timedelta
import random

DB_PATH=os.path.join(os.path.dirname(__file__), "..", "instance", "database.db")


def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables(conn: sqlite3.Connection):
    cursor=conn.cursor()
    cursor.executescript("""
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS departments;
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT NOT NULL
        );
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            salary REAL NOT NULL,
            hire_date DATE NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('active', 'completed', 'overdue')),
            deadline DATE NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
    """)
    conn.commit()

def seed_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    # --- Departments ---
    departments = [
        ("Engineering", "New York"),
        ("Marketing", "San Francisco"),
        ("Sales", "Chicago"),
        ("Human Resources", "New York"),
        ("Finance", "Boston"),
    ]
    cursor.executemany("INSERT INTO departments (name, location) VALUES (?, ?)", departments)
    # --- Employees (20 rows) ---
    first_names = [
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace",
        "Hank", "Ivy", "Jack", "Karen", "Leo", "Mona", "Nathan",
        "Olivia", "Paul", "Quinn", "Rachel", "Steve", "Tina",
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
        "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
        "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin",
    ]
    random.seed(42)
    employees = []
    for i, first in enumerate(first_names):
        last = last_names[i]
        dept_id = random.randint(1, 5)
        salary = round(random.uniform(55000, 150000), 2)
        # hire dates between 2020-01-01 and 2024-06-01
        start = date(2020, 1, 1)
        offset = random.randint(0, 1600)
        hire_date = start + timedelta(days=offset)
        employees.append((f"{first} {last}", dept_id, salary, hire_date.isoformat()))

    cursor.executemany(
        "INSERT INTO employees (name, department_id, salary, hire_date) VALUES (?, ?, ?, ?)",
        employees,
    )
    # --- Projects (20 rows) ---
    project_names = [
        "Website Redesign", "Mobile App v2", "Data Pipeline", "CRM Integration",
        "SEO Overhaul", "Cloud Migration", "Chatbot MVP", "Analytics Dashboard",
        "Payment Gateway", "Onboarding Flow", "API Platform", "Email Campaign",
        "Security Audit", "Performance Tuning", "Inventory System",
        "Customer Portal", "HR Automation", "Sales Forecasting",
        "Brand Refresh", "DevOps Pipeline",
    ]
    statuses = ["active", "completed", "overdue"]
    projects = []
    for i, pname in enumerate(project_names):
        emp_id = random.randint(1, 20)
        status = random.choice(statuses)
        if status == "overdue":
            deadline = date.today() - timedelta(days=random.randint(10, 120))
        elif status == "completed":
            deadline = date.today() - timedelta(days=random.randint(1, 200))
        else:
            deadline = date.today() + timedelta(days=random.randint(10, 180))
        projects.append((pname, emp_id, status, deadline.isoformat()))

    cursor.executemany(
        "INSERT INTO projects (name, employee_id, status, deadline) VALUES (?, ?, ?, ?)",
        projects,
    )
    conn.commit()

def init_db():
    """Create and seed the database. Safe to call multiple times (recreates)."""
    conn = get_connection()
    create_tables(conn)
    seed_data(conn)
    conn.close()
    print(f"Database created and seeded at {DB_PATH}")

if __name__ == "__main__":
    init_db()