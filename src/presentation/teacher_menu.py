from src.domain.errors import LMSError


class TeacherMenu:
    def __init__(self, user, course_service, lesson_service, assignment_service):
        self.user = user
        self.courses = course_service
        self.lessons = lesson_service
        self.assignments = assignment_service

    def run(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the instructor portal")

        while True:
            print("""
            Instructor menu
            1. Create a course
            2. View my courses
            3. Update a course
            4. Delete a course
            5. View students in a course
            6. Manage lessons
            7. Manage assignments

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
            elif choice == "5":
                self.view_course_students()
            elif choice == "6":
                self.lesson_menu()
            elif choice == "7":
                self.assignment_menu()
            elif choice == "8":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")

    
# courses
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

#   lessons

    def lesson_menu(self):
        while True:
            print("""
            Lesson menu
            1. Add a lesson
            2. View lessons in a course
            3. Update a lesson
            4. Delete a lesson
            5. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.add_lesson()
            elif choice == "2":
                self.view_lessons()
            elif choice == "3":
                self.update_lesson()
            elif choice == "4":
                self.delete_lesson()
            elif choice == "5":
                break
            else:
                print("Invalid choice.")

    def add_lesson(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        title = input("Lesson title: ")
        content = input("Lesson text (optional): ")
        video_url = input("Video link (optional): ")

        raw_order = input("Position (press Enter for the next free one): ").strip()
        if raw_order and not raw_order.isdigit():
            print("Error: position must be a number.")
            return
        lesson_order = int(raw_order) if raw_order else None

        try:
            self.lessons.add_lesson(self.user, course_id, title, content, video_url, lesson_order)
            print("Lesson added.")
        except LMSError as e:
            print(f"Error: {e}")

    def view_lessons(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            lessons = self.lessons.list_lessons(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not lessons:
            print("This course has no lessons yet.")
            return

        print(f"\n{'Pos':<5}{'ID':<5}{'Title':<35}{'Video'}")
        for lesson in lessons:
            print(
                f"{lesson['lesson_order']:<5}{lesson['id']:<5}{lesson['title']:<35}"
                f"{lesson['video_url'] or '-'}"
            )

    def _pick_lesson(self):
        raw_course = input("Enter the ID of the course: ")
        if not raw_course.isdigit():
            print("Error: please enter a number.")
            return None
        course_id = int(raw_course)

        try:
            lessons = self.lessons.list_lessons(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return None

        if not lessons:
            print("This course has no lessons yet.")
            return None

        print(f"\n{'Pos':<5}{'ID':<5}{'Title'}")
        for lesson in lessons:
            print(f"{lesson['lesson_order']:<5}{lesson['id']:<5}{lesson['title']}")

        raw_lesson = input("Enter the ID of the lesson: ")
        if not raw_lesson.isdigit():
            print("Error: please enter a number.")
            return None

        current = next((item for item in lessons if item["id"] == int(raw_lesson)), None)
        if current is None:
            print("Error: that lesson is not in this course.")
        return current

    def update_lesson(self):
        current = self._pick_lesson()
        if current is None:
            return

        print("Press Enter to keep the current value.")
        title = input(f"Title [{current['title']}]: ") or current["title"]
        content = input("Lesson text (Enter to keep): ") or (current["content"] or "")
        video_url = input(f"Video link [{current['video_url'] or '-'}]: ") or (current["video_url"] or "")

        try:
            self.lessons.update_lesson(self.user, current["id"], title, content, video_url)
            print("Lesson updated.")
        except LMSError as e:
            print(f"Error: {e}")

    def delete_lesson(self):
        current = self._pick_lesson()
        if current is None:
            return

        if input(f"Delete lesson '{current['title']}'? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            self.lessons.delete_lesson(self.user, current["id"])
            print("Lesson deleted.")
        except LMSError as e:
            print(f"Error: {e}")

    # assignments
    def assignment_menu(self):
        while True:
            print("""
            Assignment menu
            1. Create an assignment
            2. View assignments in a course
            3. Update an assignment
            4. Delete an assignment
            5. View submissions
            6. Grade a submission
            7. Release marks
            8. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.create_assignment()
            elif choice == "2":
                self.view_assignments()
            elif choice == "3":
                self.update_assignment()
            elif choice == "4":
                self.delete_assignment()
            elif choice == "5":
                self.view_submissions()
            elif choice == "6":
                self.grade_submission()
            elif choice == "7":
                self.release_marks()
            elif choice == "8":
                break
            else:
                print("Invalid choice.")

    def create_assignment(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        title = input("Assignment title: ")
        description = input("Instructions (optional): ")
        due_date = input("Due date, YYYY-MM-DD (optional): ")

        raw_marks = input("Maximum marks (press Enter for 100): ").strip()
        if raw_marks and not raw_marks.isdigit():
            print("Error: marks must be a number.")
            return
        max_marks = int(raw_marks) if raw_marks else 100

        try:
            assignment_id = self.assignments.create_assignment(
                self.user, course_id, title, description, due_date, max_marks
            )
            print(f"Assignment created with ID {assignment_id}.")
        except LMSError as e:
            print(f"Error: {e}")

    def view_assignments(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            assignments = self.assignments.list_assignments(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not assignments:
            print("This course has no assignments yet.")
            return

        self._print_assignments(assignments)

    def _print_assignments(self, assignments):
        print(f"\n{'ID':<5}{'Title':<30}{'Due':<13}{'Marks'}")
        for a in assignments:
            due = a["due_date"].strftime("%Y-%m-%d") if a["due_date"] else "-"
            print(f"{a['id']:<5}{a['title']:<30}{due:<13}{a['max_marks']}")

    def _pick_assignment(self):
        raw_course = input("Enter the ID of the course: ")
        if not raw_course.isdigit():
            print("Error: please enter a number.")
            return None
        course_id = int(raw_course)

        try:
            assignments = self.assignments.list_assignments(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return None

        if not assignments:
            print("This course has no assignments yet.")
            return None

        self._print_assignments(assignments)

        raw_assignment = input("Enter the ID of the assignment: ")
        if not raw_assignment.isdigit():
            print("Error: please enter a number.")
            return None

        current = next((a for a in assignments if a["id"] == int(raw_assignment)), None)
        if current is None:
            print("Error: that assignment is not in this course.")
        return current

    def update_assignment(self):
        current = self._pick_assignment()
        if current is None:
            return

        current_due = current["due_date"].strftime("%Y-%m-%d") if current["due_date"] else ""

        print("Press Enter to keep the current value.")
        title = input(f"Title [{current['title']}]: ") or current["title"]
        description = input("Instructions (Enter to keep): ") or (current["description"] or "")
        due_date = input(f"Due date [{current_due or '-'}]: ") or current_due

        raw_marks = input(f"Maximum marks [{current['max_marks']}]: ").strip()
        if raw_marks and not raw_marks.isdigit():
            print("Error: marks must be a number.")
            return
        max_marks = int(raw_marks) if raw_marks else current["max_marks"]

        try:
            self.assignments.update_assignment(
                self.user, current["id"], title, description, due_date, max_marks
            )
            print("Assignment updated.")
        except LMSError as e:
            print(f"Error: {e}")

    def delete_assignment(self):
        current = self._pick_assignment()
        if current is None:
            return

        if input(f"Delete '{current['title']}' and all its submissions? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            self.assignments.delete_assignment(self.user, current["id"])
            print("Assignment deleted.")
        except LMSError as e:
            print(f"Error: {e}")

    def view_submissions(self):
        current = self._pick_assignment()
        if current is None:
            return

        try:
            submissions = self.assignments.view_submissions(self.user, current["id"])
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not submissions:
            print("No submissions yet.")
            return

        print(f"\n{'ID':<5}{'Student':<25}{'Submitted':<18}{'Score':<10}{'Released':<10}{'Link'}")
        for s in submissions:
            name = f"{s['first_name']} {s['last_name']}"
            when = s["submitted_at"].strftime("%Y-%m-%d %H:%M")
            score = f"{s['score']}/{current['max_marks']}" if s["score"] is not None else "-"
            released = "yes" if s["released"] else "no"
            print(f"{s['id']:<5}{name:<25}{when:<18}{score:<10}{released:<10}{s['submission_link']}")

    def grade_submission(self):
        current = self._pick_assignment()
        if current is None:
            return

        try:
            submissions = self.assignments.view_submissions(self.user, current["id"])
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not submissions:
            print("No submissions yet.")
            return

        print(f"\n{'ID':<5}{'Student':<25}{'Score':<10}{'Link'}")
        for s in submissions:
            name = f"{s['first_name']} {s['last_name']}"
            score = f"{s['score']}/{current['max_marks']}" if s["score"] is not None else "-"
            print(f"{s['id']:<5}{name:<25}{score:<10}{s['submission_link']}")

        raw_id = input("Enter the ID of the submission to grade: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        submission_id = int(raw_id)

        raw_score = input(f"Score (0 to {current['max_marks']}): ").strip()
        try:
            score = float(raw_score)
        except ValueError:
            print("Error: score must be a number.")
            return

        feedback = input("Feedback (optional): ")

        try:
            self.assignments.grade_submission(self.user, submission_id, score, feedback)
            print("Submission graded. Use 'Release marks' to show it to the student.")
        except LMSError as e:
            print(f"Error: {e}")

    def release_marks(self):
        current = self._pick_assignment()
        if current is None:
            return

        if input(f"Release all graded marks for '{current['title']}'? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            count = self.assignments.release_marks(self.user, current["id"])
            print(f"Released {count} mark(s).")
        except LMSError as e:
            print(f"Error: {e}")
