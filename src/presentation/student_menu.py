from src.domain.errors import LMSError


class StudentMenu:
    def __init__(self, user, enrollment_service, lesson_service, assignment_service):
        self.user = user
        self.enrollments = enrollment_service
        self.lessons = lesson_service
        self.assignments = assignment_service

    def run(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the student portal")

        while True:
            print("""
            Student menu
            1. Browse courses
            2. Enroll in a course
            3. My courses
            4. View lessons for a course

            8. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.browse_courses()
            elif choice == "2":
                self.enroll_in_course()
            elif choice == "3":
                self.view_enrolled_courses()
            elif choice == "4":
                self.read_course_lessons()
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

    def read_course_lessons(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            lessons = self.lessons.read_lessons(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not lessons:
            print("This course has no lessons yet.")
            return

        for lesson in lessons:
            print(f"\nLesson {lesson['lesson_order']}: {lesson['title']}")
            if lesson["video_url"]:
                print(f"Video: {lesson['video_url']}")
            if lesson["content"]:
                print(lesson["content"])
