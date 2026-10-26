from src.domain.enums import Role
from src.domain.errors import NotFound, PermissionDenied, ValidationError
from src.services.permissions import require_role


class LessonService:
    def __init__(self, lesson_repo, course_repo, enrollment_repo):
        self.lesson_repo = lesson_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo

    @require_role(Role.INSTRUCTOR)
    def add_lesson(self, acting_user, course_id, title, content, video_url, lesson_order=None):
        title = title.strip()
        if not title:
            raise ValidationError("Lesson title is required.")

        content = content.strip() or None
        video_url = video_url.strip() or None

        self._get_owned_course(acting_user, course_id)

        if lesson_order is None:
            lesson_order = self.lesson_repo.next_order(course_id)
        elif lesson_order < 1:
            raise ValidationError("Lesson position must be 1 or higher.")

        return self.lesson_repo.create(course_id, title, content, video_url, lesson_order)

    @require_role(Role.INSTRUCTOR)
    def list_lessons(self, acting_user, course_id):
        self._get_owned_course(acting_user, course_id)
        return self.lesson_repo.list_by_course(course_id)

    @require_role(Role.INSTRUCTOR)
    def update_lesson(self, acting_user, lesson_id, title, content, video_url):
        title = title.strip()
        if not title:
            raise ValidationError("Lesson title is required.")

        content = content.strip() or None
        video_url = video_url.strip() or None

        self._get_owned_lesson(acting_user, lesson_id)

        self.lesson_repo.update(lesson_id, title, content, video_url)

    @require_role(Role.INSTRUCTOR)
    def delete_lesson(self, acting_user, lesson_id):
        self._get_owned_lesson(acting_user, lesson_id)
        self.lesson_repo.delete(lesson_id)

    @require_role(Role.STUDENT)
    def read_lessons(self, acting_user, course_id):
        if self.course_repo.get_by_id(course_id) is None:
            raise NotFound("Course is not found")

        if not self.enrollment_repo.exists(acting_user.id, course_id):
            raise PermissionDenied("Enroll in this course to see its lessons.")

        return self.lesson_repo.list_by_course(course_id)

    def _get_owned_course(self, acting_user, course_id):
        course = self.course_repo.get_by_id(course_id)
        if course is None:
            raise NotFound("Course is not found")
        if course["instructor_id"] != acting_user.id:
            raise PermissionDenied("You are not authorized to do this")
        return course

    def _get_owned_lesson(self, acting_user, lesson_id):
        lesson = self.lesson_repo.get_by_id(lesson_id)
        if lesson is None:
            raise NotFound("Lesson is not found")
        self._get_owned_course(acting_user, lesson["course_id"])
        return lesson
