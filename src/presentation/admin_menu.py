from src.domain.enums import Role
from src.domain.errors import LMSError
from src.presentation.profile_menu import ProfileMenu


class AdminMenu:
    def __init__(self, user, user_service, report_service):
        self.user = user
        self.users = user_service
        self.reports = report_service
        self.profile_menu = ProfileMenu(user, user_service)

    def run(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the admin portal")

        while True:
            print("""
            Admin menu
            1. View all users
            2. Search or filter users
            3. Change a user's role
            4. Disable or reactivate an account
            5. View statistics
            6. Export summary report (CSV)
            7. My profile

            8. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.view_users()
            elif choice == "2":
                self.search_users()
            elif choice == "3":
                self.change_user_role()
            elif choice == "4":
                self.toggle_account()
            elif choice == "5":
                self.view_statistics()
            elif choice == "6":
                self.export_summary()
            elif choice == "7":
                self.profile_menu.run()
            elif choice == "8":
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

        self._print_users(users)

    def search_users(self):
        term = input("Name or email contains (Enter for any): ")

        print("Role: 1. student  2. instructor  3. admin  (Enter for any)")
        roles = {"1": Role.STUDENT, "2": Role.INSTRUCTOR, "3": Role.ADMIN}
        raw_role = input("Enter your choice: ")
        if raw_role and raw_role not in roles:
            print("Error: invalid choice.")
            return
        role = roles[raw_role].value if raw_role else None

        print("Status: 1. active  2. disabled  (Enter for any)")
        statuses = {"1": True, "2": False}
        raw_status = input("Enter your choice: ")
        if raw_status and raw_status not in statuses:
            print("Error: invalid choice.")
            return
        active = statuses[raw_status] if raw_status else None

        try:
            users = self.users.search_users(self.user, term, role, active)
        except LMSError as e:
            print(f"Error: {e}")
            return

        self._print_users(users)

    def toggle_account(self):
        raw_id = input("Enter the ID of the user: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        user_id = int(raw_id)

        print("1. Disable  2. Reactivate")
        action = {"1": False, "2": True}.get(input("Enter your choice: "))
        if action is None:
            print("Error: invalid choice.")
            return

        verb = "reactivate" if action else "disable"
        if input(f"Really {verb} the user with the ID <{user_id}>? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            self.users.set_active(self.user, user_id, action)
            print("Account reactivated." if action else "Account disabled.")
        except LMSError as e:
            print(f"Error: {e}")

    def _print_users(self, users):
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

    def export_summary(self):
        try:
            path = self.reports.export_overview(self.user)
            print(f"Report saved to: {path}")
        except LMSError as e:
            print(f"Error: {e}")

    def view_statistics(self):
        try:
            stats = self.reports.get_overview(self.user)
            top = self.reports.top_courses(self.user, 5)
        except LMSError as e:
            print(f"Error: {e}")
            return

        print("\nPlatform overview")
        print(f"  Users:        {stats['total_users']}  "
              f"(students {stats['students']}, instructors {stats['instructors']}, "
              f"admins {stats['admins']})")
        print(f"  Courses:      {stats['courses']}")
        print(f"  Enrollments:  {stats['enrollments']}")
        print(f"  Lessons:      {stats['lessons']}")
        print(f"  Assignments:  {stats['assignments']}  (submissions {stats['submissions']})")
        print(f"  Quizzes:      {stats['quizzes']}  (questions {stats['questions']}, "
              f"attempts {stats['quiz_attempts']})")

        if not top:
            print("\nNo courses yet.")
            return

        print(f"\n{'Top courses by enrollment':<35}{'Instructor':<25}{'Enrolled'}")
        for c in top:
            instructor = f"{c['first_name']} {c['last_name']}"
            print(f"{c['title']:<35}{instructor:<25}{c['enrollments']}")
