from db_ops import *
from db_setup import *

def admin_menu():
    while True:
        print("1. Add Company\n 2. View All Students\n3. View Applicants for Company\n4. Update Application Status\n5. Issue Offer\n6. View Highest Package\n7. Department-wise Placement Count\n8. Top 3 Hiring Companies\n9. Logout")
        ch = int(input("Enter a choice: "))
        if(ch==1):
            setup_companytab()
            print(" MANAGE COMPANY ")
            add_a_company()
        elif(ch==2):
            print("All students")
        elif(ch==3):
            print("")
        elif(ch==4):
            print("")
        elif(ch==5):
            print("")
        elif(ch==6):
            print("")
        elif(ch==7):
            print("")
        elif(ch==8):
            print("")
        elif(ch==9):
            break
        else:
            print("Enter a valid choice")
def add_stu():
    u_name = input("Enter username:")
    u_id = int(input("Enter StudentID/StaffID: "))
    u_pass = input("Enter password: ")
    u_role = input("Give role: ")
    add_students(u_name, u_pass, u_role, u_id)

def remove_stu():
    u_id = int(input("Enter your StudentID/StaffID to delete: "))
    remove_student(u_id)

def add_a_company():
    c_name = input("Company name: ")
    role = input("Role offered: ")
    try:
        min_cgpa = float(input("Minimum CGPA: "))
    except ValueError:
        print("Invalid CGPA")
        return
    package = float(input("Package: "))
    add_company(c_name, role, min_cgpa, package)

