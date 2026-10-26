from src.domain.errors import LMSError, UnverifiedError
from src.services import validators


class AuthMenu:
    def __init__(self, auth_service):
        self.auth = auth_service

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
            user = self.auth.login(email, password)
        except UnverifiedError as e:
            print(f"Email not verified: {e}")
            if input("Send a verification code now? (y/n): ").lower() == "y":
                self.verify_email(email)
            return None
        except LMSError as e:
            print(f"Error: {e}")
            return None

        print(f"Login successful. Welcome {user.first_name}.")
        return user
