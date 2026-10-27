from src.domain.errors import LMSError


class LessonsMenu:
    def __init__(self, user, lesson_service):
        self.user = user
        self.lessons = lesson_service

    def run(self):
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
