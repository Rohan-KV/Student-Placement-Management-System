from db_ops import *
from admin_menu import *
from db_setup import *


print("*****PLACEMENT MANAGEMENT SYSTEM*****")

def user_auth():
    auth_user = input("Enter your username: ")
    auth_password = input("Enter your password: ")
    res = validate_user(auth_user, auth_password)
    if(res==0):
        print("No username found!")
    elif(res==1):
        print("Login Success!")
        role = getrole(auth_user)
        if(role=="Admin"):
            admin_menu()
        else:
            print("To be impelemted")
    else:
        print("wrong password!")

while True:
    print("1. Login\n 2. Exit")
    ch = int(input("Enter your choice: "))
    if(ch==1):
       print("Enter your username and password")
       user_auth() 
    else:
        break





