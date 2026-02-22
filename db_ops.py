import sqlite3
import bcrypt
def setup_usertab():
    conn = sqlite3.connect('db/student.db')
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, stud_id INTEGER UNIQUE, u_name VARCHAR(30), pass_hash VARCHAR(60), role VARCHAR(30))''')
    conn.commit()
    conn.close()

def add_students(u_name, u_pass, u_role, u_id):
    conn = sqlite3.connect('db/student.db')
    c=conn.cursor()
    pass_bytes = u_pass.encode('utf-8')
    hashed_pass = bcrypt.hashpw(pass_bytes, bcrypt.gensalt())
    c.execute("INSERT INTO users(u_name, pass_hash, role, stud_id) VALUES(?, ?, ?, ?)", (u_name, hashed_pass, u_role, u_id))
    print("The user ", u_name, " is added")
    conn.commit()
    conn.close()

def validate_user(auth_user, auth_password):
    conn = sqlite3.connect('db/student.db')
    c=conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE u_name = ?", (auth_user,))
    user_count = c.fetchone()[0]
    if user_count == 0:
        conn.close()
        return 0
    else:
        c.execute("SELECT pass_hash FROM users WHERE u_name = ?", (auth_user,))
        stored_hash = c.fetchone()[0]
        conn.close()
        if bcrypt.checkpw(auth_password.encode('utf-8'), stored_hash):
            return 1
        else:
            return 2
        
def getrole(auth_user):
    conn = sqlite3.connect('db/student.db')
    c=conn.cursor()
    c.execute("SELECT role FROM users WHERE u_name = ?", (auth_user,))
    res = c.fetchone()
    conn.close()
    return res[0]

def remove_student(u_id):
    conn = sqlite3.connect('db/student.db')
    c=conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE stud_id = ?", (u_id,))
    count = c.fetchone()[0]
    if count == 0:
        print("Student ID not found!")
        conn.close()
        return
    c.execute("DELETE FROM users WHERE stud_id = ?", (u_id,))
    conn.commit()
    print("Student removed successfully!")
    conn.close()