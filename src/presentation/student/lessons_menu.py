from src.domain.errors import LMSError


class LessonsMenu:
    def __init__(self, user, lesson_service):
        self.user = user
        self.lessons = lesson_service

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
