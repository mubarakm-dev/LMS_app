from src.domain.enums import Role
from src.domain.errors import LMSError


class AdminMenu:
    def __init__(self, user, user_service):
        self.user = user
        self.users = user_service

    def run(self):
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
