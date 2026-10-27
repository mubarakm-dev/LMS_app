from src.domain.errors import LMSError


class CoursesMenu:
    def __init__(self, user, enrollment_service):
        self.user = user
        self.enrollments = enrollment_service

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
