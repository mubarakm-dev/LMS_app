from src.domain.enums import Role
from src.domain.errors import LMSError


class AdminMenu:
    def __init__(self, user, user_service, report_service):
        self.user = user
        self.users = user_service
        self.reports = report_service

    def run(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the admin portal")

        while True:
            print("""
            Admin menu
            1. View all users
            2. Change a user's role
            3. View statistics

            4. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.view_users()
            elif choice == "2":
                self.change_user_role()
            elif choice == "3":
                self.view_statistics()
            elif choice == "4":
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
