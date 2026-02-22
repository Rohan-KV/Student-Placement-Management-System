from db_ops import *
setup_usertab()

def add_stu():
    u_name = input("Enter username:")
    u_id = int(input("Enter StudentID/StaffID: "))
    u_pass = input("Enter password: ")
    u_role = input("Give role: ")
    add_students(u_name, u_pass, u_role, u_id)

add_stu()