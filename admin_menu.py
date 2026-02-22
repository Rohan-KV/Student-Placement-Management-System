from db_ops import *

def admin_menu():
    while True:
        print("1. Add student\n2. Remove student\n3. Exit")
        ch = int(input("Enter a choice: "))
        if(ch==1):
            add_stu()
        elif(ch==2):
            remove_stu()
        else:
            break



def add_stu():
    u_name = input("Enter username:")
    u_id = int(input("Enter StudentID/StaffID: "))
    u_pass = input("Enter password: ")
    u_role = input("Give role: ")
    add_students(u_name, u_pass, u_role, u_id)

def remove_stu():
    u_id = int(input("Enter your StudentID/StaffID to delete: "))
    remove_student(u_id)

