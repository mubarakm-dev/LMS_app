from src.domain.enums import Role
from src.domain.errors import DuplicateError, NotFound
from src.services.permissions import require_role


class EnrollmentService:
    def __init__(self, enrollment_repo, course_repo):
        self.enrollment_repo = enrollment_repo
        self.course_repo = course_repo

    @require_role(Role.STUDENT)
    def browse_courses(self, acting_user):
        return self.course_repo.list_all()

    @require_role(Role.STUDENT)
    def enroll(self, acting_user, course_id):
        course = self.course_repo.get_by_id(course_id)
        if course is None:
            raise NotFound("Course not found.")

        if self.enrollment_repo.exists(acting_user.id, course_id):
            raise DuplicateError("You are already enrolled in this course.")

        return self.enrollment_repo.create(acting_user.id, course_id)

    @require_role(Role.STUDENT)
    def my_courses(self, acting_user):
        return self.enrollment_repo.list_by_student(acting_user.id)
