from src.domain.errors import LMSError, UnverifiedError
from src.services import validators 
from src.domain.enums import Role

class App:

    def __init__(self, auth_service, user_service):
        self.auth = auth_service
        self.users = user_service
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

        while True:
            print("""
            Admin menu
            1. View all users
            2. Change a user's role
            3. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.view_users()
            elif choice == "2":
                self.change_user_role()
            elif choice == "3":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")

    def view_users(self):
        try:
            users = self.users.list_users(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not users:
            print("No users found.")
            return

        print(f"\n{'ID':<5}{'Name':<25}{'Email':<30}{'Role':<12}{'Verified':<10}{'Active'}")
        for u in users:
            name = f"{u['first_name']} {u['last_name']}"
            print(
                f"{u['id']:<5}{name:<25}{u['email']:<30}{u['role']:<12}"
                f"{'yes' if u['is_verified'] else 'no':<10}{'yes' if u['is_active'] else 'no'}"
            )

    def change_user_role(self):
        raw_id = input("Enter the ID of the user: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        user_id = int(raw_id)

        print("New role: 1. student  2. instructor  3. admin")
        roles = {"1": Role.STUDENT, "2": Role.INSTRUCTOR, "3": Role.ADMIN}
        new_role = roles.get(input("Enter your choice: "))
        if new_role is None:
            print("Error: invalid choice.")
            return

        if input(f"Change user with the ID <{user_id}> to {new_role.value}? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            self.users.change_role(self.user, user_id, new_role.value)
            print("Role updated.")
        except LMSError as e:
            print(f"Error: {e}")

        
        
    
    