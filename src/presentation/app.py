from src.domain.errors import LMSError, UnverifiedError
from src.services import validators 
from src.domain.enums import Role

class App:

    def __init__(self, auth_service):
        self.auth = auth_service
        self.user = None

    def main_menu(self):
        while True:
            print("""Welcome to SQI Learning Centre

            1. Register
            2. Login
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

        self.verify_email(email)

    def verify_email(self, email):
        try:
            self.auth.send_verification_code(email)
            print("A verification code has been sent to your email.")
        except LMSError as e:
            print(f"Error: {e}")
            return

        while True:
            code = input("Enter the verification code (or press Enter to skip): ")
            if code == "":
                print("You can verify later by logging in.")
                return
            try:
                self.auth.verify_code(email, code)
                print("Email verified successfully. You can now log in.")
                return
            except LMSError as e:
                print(f"Error: {e}")
                if "request a new" in str(e) or "expired" in str(e):
                    return

    def login(self):
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        try:
            self.user = self.auth.login(email, password)
            print(f"Login successful. Welcome {self.user.first_name}.")
        except UnverifiedError as e:
            print(f"Email not verified: {e}")
            if input("Send a verification code now? (y/n): ").lower() == "y":
                self.verify_email(email)
            return
        except LMSError as e:
            print(f"Error: {e}")
            return

  

        if self.user.role == Role.STUDENT:
            self.student_dashboard()
        elif self.user.role == Role.INSTRUCTOR:
            self.instructor_dashboard()
        elif self.user.role == Role.ADMIN:
            self.admin_dashboard()

        self.user = None

    def student_dashboard(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the student portal")

    def instructor_dashboard(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the instructor portal")

    def admin_dashboard(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the admin portal")

        
        
    
    