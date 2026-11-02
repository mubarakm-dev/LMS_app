from src.domain.errors import LMSError


class ProfileMenu:
    def __init__(self, user, user_service):
        self.user = user
        self.users = user_service

    def run(self):
        while True:
            print("""
            My profile
            1. View my profile
            2. Update my name
            3. Change my password
            4. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.view_profile()
            elif choice == "2":
                self.update_name()
            elif choice == "3":
                self.change_password()
            elif choice == "4":
                break
            else:
                print("Invalid choice.")

    def view_profile(self):
        try:
            p = self.users.get_profile(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        print(f"\nName:     {p['first_name']} {p['last_name']}")
        print(f"Email:    {p['email']}")
        print(f"Role:     {p['role']}")
        print(f"Verified: {'yes' if p['is_verified'] else 'no'}")

    def update_name(self):
        print("Press Enter to keep the current value.")
        first = input(f"First name [{self.user.first_name}]: ") or self.user.first_name
        last = input(f"Last name [{self.user.last_name}]: ") or self.user.last_name

        try:
            self.users.update_profile(self.user, first, last)
            print("Profile updated.")
        except LMSError as e:
            print(f"Error: {e}")

    def change_password(self):
        current = input("Current password: ")
        new = input("New password: ")
        confirm = input("Confirm new password: ")

        try:
            self.users.change_password(self.user, current, new, confirm)
            print("Password changed.")
        except LMSError as e:
            print(f"Error: {e}")
