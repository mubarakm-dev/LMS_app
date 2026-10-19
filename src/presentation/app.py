from src.domain.errors import LMSError
from src.services.validators 

class App:

    def __init__(self, auth_service):
        self.auth = auth_service
        self.user = None

    def main_menu():
        while True:
            print("""Welcome to SQI Learning Centre

            1. Login
            2. Register
            3. Exit
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            elif choice == "3":
                print("Thank you for using SQI LMS")
                break
            else:
                print("Invalid choice.")



    def register(self):
        first_name = input("Enter your first name: ")
        last_name = input("Enter your last name: ")
        email = input("Enter your email: ")

        if input("Suggest a strong password? (y/n): ").lower() == "y":
            print("Suggested:", validators.suggest_password())

        password = input("Enter your password: ")
        confirm_password = input("Confirm password: ")


        try:
            self.auth.register(first_name, last_name, email, password, confirm_password)
            print("Account Created Successfully")
        except LMSError as e:
            print(f"Error: {e}")
            return


    def login(self):
        email = input("Enter your email: ")


        
        
    
    