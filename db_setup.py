import sqlite3


def setup_usertab():
    conn = sqlite3.connect('db/student.db')
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, stud_id INTEGER UNIQUE, u_name VARCHAR(30), pass_hash VARCHAR(60), role VARCHAR(30))''')
    conn.commit()
    conn.close()

def setup_companytab():
    conn = sqlite3.connect('db/student.db')
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS company (company_id INTEGER PRIMARY KEY AUTOINCREMENT, company_name VARCHAR(50) NOT NULL, role_offered VARCHAR(50) NOT NULL, min_cgpa REAL NOT NULL CHECK (min_cgpa <= 10 AND min_cgpa > 0), package REAL NOT NULL CHECK(package > 0))''')
    conn.commit()
    conn.close()


setup_usertab()
setup_companytab()