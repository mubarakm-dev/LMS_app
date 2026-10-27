from src.domain.errors import LMSError


class CoursesMenu:
    def __init__(self, user, course_service):
        self.user = user
        self.courses = course_service

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

    def view_course_students(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            students = self.courses.list_course_students(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not students:
            print("No students are enrolled in this course yet.")
            return

        print(f"\n{'ID':<5}{'Name':<25}{'Email':<30}{'Status':<12}{'Enrolled'}")
        for s in students:
            name = f"{s['first_name']} {s['last_name']}"
            enrolled = s["enrolled_at"].strftime("%Y-%m-%d")
            print(f"{s['id']:<5}{name:<25}{s['email']:<30}{s['status']:<12}{enrolled}")
