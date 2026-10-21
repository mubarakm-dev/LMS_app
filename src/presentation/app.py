from src.domain.errors import LMSError, UnverifiedError
from src.services import validators 
from src.domain.enums import Role

class App:

    def __init__(self, auth_service, user_service, course_service, enrollment_service):
        self.auth = auth_service
        self.users = user_service
        self.courses = course_service
        self.enrollments = enrollment_service
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

        while True:
            print("""
            Student menu
            1. Browse courses
            2. Enroll in a course
            3. My courses

            8. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.browse_courses()
            elif choice == "2":
                self.enroll_in_course()
            elif choice == "3":
                self.view_enrolled_courses()
            elif choice == "8":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")

    def browse_courses(self):
        try:
            courses = self.enrollments.browse_courses(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not courses:
            print("No courses are available yet.")
            return

        print(f"\n{'ID':<5}{'Title':<30}{'Instructor':<25}{'Duration':<15}")
        for c in courses:
            instructor = f"{c['instructor_first_name']} {c['instructor_last_name']}"
            print(f"{c['id']:<5}{c['title']:<30}{instructor:<25}{c['duration'] or '-':<15}")

    def enroll_in_course(self):
        raw_id = input("Enter the ID of the course to enroll in: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            self.enrollments.enroll(self.user, course_id)
            print("Enrolled successfully.")
        except LMSError as e:
            print(f"Error: {e}")

    def view_enrolled_courses(self):
        try:
            courses = self.enrollments.my_courses(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not courses:
            print("You are not enrolled in any courses yet.")
            return

        print(f"\n{'ID':<5}{'Title':<30}{'Instructor':<25}{'Status':<12}")
        for c in courses:
            instructor = f"{c['instructor_first_name']} {c['instructor_last_name']}"
            print(f"{c['id']:<5}{c['title']:<30}{instructor:<25}{c['status']:<12}")

    def instructor_dashboard(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the instructor portal")

        while True:
            print("""
            Instructor menu
            1. Create a course
            2. View my courses
            3. Update a course
            4. Delete a course

            8. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.create_course()
            elif choice == "2":
                self.view_my_courses()
            elif choice == "3":
                self.update_course()
            elif choice == "4":
                self.delete_course()
            elif choice == "8":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")

    def create_course(self):
        title = input("Course title: ")
        description = input("Description (optional): ")
        duration = input("Duration, e.g. 6 weeks (optional): ")

        try:
            course_id = self.courses.create_course(self.user, title, description, duration)
            print(f"Course created with ID {course_id}.")

        except LMSError as e:
            print(f"Error: {e}")

    def view_my_courses(self):
        try:
            courses = self.courses.list_my_courses(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not courses:
            print("You have no courses yet.")
            return

        print(f"\n{'ID':<5}{'Title':<30}{'Duration':<15}{'Description'}")
        for c in courses:
            print(
                f"{c['id']:<5}{c['title']:<30}{c['duration'] or '-':<15}{c['description'] or '-'}"
            )

    def update_course(self):
        raw_id = input("Enter the ID of the course to update: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            courses = self.courses.list_my_courses(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        current = next((c for c in courses if c["id"] == course_id), None)
        if current is None:
            print("Error: you have no course with that ID.")
            return

        print("Press Enter to keep the current value.")
        title = input(f"Title [{current['title']}]: ") or current["title"]
        description = input(f"Description [{current['description'] or '-'}]: ") or (current["description"] or "")
        duration = input(f"Duration [{current['duration'] or '-'}]: ") or (current["duration"] or "")

        try:
            self.courses.update_course(self.user, course_id, title, description, duration)
            print("Course updated.")
        except LMSError as e:
            print(f"Error: {e}")


        

    def delete_course(self):
        raw_id = input("Enter the ID of the course to delete: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            courses = self.courses.list_my_courses(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return
        current = next((c for c in courses if c["id"] == course_id), None)
        if current is None:
            print("Error: you have no course with that ID.")
            return

        if input(f"Delete '{current['title']}' and everything in it? (y/n): ").lower() != "y":
            print("Cancelled.")
            return
        try:
            self.courses.delete_course(self.user, course_id)
            print("Course deleted.")
        except LMSError as e:
            print(f"Error: {e}")



    





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

        
        
    
    