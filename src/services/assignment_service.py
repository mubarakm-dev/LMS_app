from datetime import date, datetime

from src.domain.enums import Role
from src.domain.errors import NotFound, PermissionDenied, ValidationError
from src.services.permissions import require_role

MAX_LINK_LENGTH = 255


class AssignmentService:
    def __init__(self, assignment_repo, submission_repo, course_repo, enrollment_repo):
        self.assignment_repo = assignment_repo
        self.submission_repo = submission_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo

    @require_role(Role.INSTRUCTOR)
    def create_assignment(self, acting_user, course_id, title, description, due_date, max_marks):
        title = title.strip()
        if not title:
            raise ValidationError("Assignment title is required.")

        description = description.strip() or None
        due_date = self._parse_due_date(due_date)
        self._check_max_marks(max_marks)

        self._get_owned_course(acting_user, course_id)

        return self.assignment_repo.create(course_id, title, description, due_date, max_marks)

    @require_role(Role.INSTRUCTOR)
    def list_assignments(self, acting_user, course_id):
        self._get_owned_course(acting_user, course_id)
        return self.assignment_repo.list_by_course(course_id)

    @require_role(Role.INSTRUCTOR)
    def update_assignment(self, acting_user, assignment_id, title, description, due_date, max_marks):
        title = title.strip()
        if not title:
            raise ValidationError("Assignment title is required.")

        description = description.strip() or None
        due_date = self._parse_due_date(due_date)
        self._check_max_marks(max_marks)

        self._get_owned_assignment(acting_user, assignment_id)

        self.assignment_repo.update(assignment_id, title, description, due_date, max_marks)

    @require_role(Role.INSTRUCTOR)
    def delete_assignment(self, acting_user, assignment_id):
        self._get_owned_assignment(acting_user, assignment_id)
        self.assignment_repo.delete(assignment_id)

    @require_role(Role.INSTRUCTOR)
    def view_submissions(self, acting_user, assignment_id):
        self._get_owned_assignment(acting_user, assignment_id)
        return self.submission_repo.list_for_assignment(assignment_id)

    @require_role(Role.INSTRUCTOR)
    def grade_submission(self, acting_user, submission_id, score, feedback):
        submission = self.submission_repo.get_by_id(submission_id)
        if submission is None:
            raise NotFound("Submission is not found")

        assignment = self._get_owned_assignment(acting_user, submission["assignment_id"])

        if score < 0 or score > assignment["max_marks"]:
            raise ValidationError(f"Score must be between 0 and {assignment['max_marks']}.")

        feedback = feedback.strip() or None
        self.submission_repo.grade(submission_id, score, feedback)

    @require_role(Role.INSTRUCTOR)
    def release_marks(self, acting_user, assignment_id):
        self._get_owned_assignment(acting_user, assignment_id)
        return self.submission_repo.release_all_graded(assignment_id)

    @require_role(Role.STUDENT)
    def list_assignments_for_student(self, acting_user, course_id):
        if self.course_repo.get_by_id(course_id) is None:
            raise NotFound("Course is not found")

        if not self.enrollment_repo.exists(acting_user.id, course_id):
            raise PermissionDenied("Enroll in this course to see its assignments.")

        return self.assignment_repo.list_by_course(course_id)

    @require_role(Role.STUDENT)
    def submit(self, acting_user, assignment_id, link):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if assignment is None:
            raise NotFound("Assignment is not found")

        if not self.enrollment_repo.exists(acting_user.id, assignment["course_id"]):
            raise PermissionDenied("Enroll in this course to submit work.")

        if assignment["due_date"] is not None and date.today() > assignment["due_date"]:
            raise ValidationError("The deadline for this assignment has passed.")

        link = link.strip()
        if not link:
            raise ValidationError("A submission link is required.")
        if not link.startswith(("http://", "https://")):
            raise ValidationError("The link must start with http:// or https://")
        if len(link) > MAX_LINK_LENGTH:
            raise ValidationError(f"The link must be {MAX_LINK_LENGTH} characters or fewer.")

        return self.submission_repo.create(assignment_id, acting_user.id, link)

    @require_role(Role.STUDENT)
    def my_submissions(self, acting_user):
        rows = self.submission_repo.list_by_student(acting_user.id)
        for row in rows:
            if not row["released"]:
                row["score"] = None
                row["feedback"] = None
        return rows

    def _parse_due_date(self, text):
        text = text.strip()
        if not text:
            return None
        try:
            due = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Due date must be in YYYY-MM-DD format.")
        if due < date.today():
            raise ValidationError("Due date cannot be in the past.")
        return due

    def _check_max_marks(self, max_marks):
        if max_marks < 1:
            raise ValidationError("Maximum marks must be 1 or higher.")

    def _get_owned_course(self, acting_user, course_id):
        course = self.course_repo.get_by_id(course_id)
        if course is None:
            raise NotFound("Course is not found")
        if course["instructor_id"] != acting_user.id:
            raise PermissionDenied("You are not authorized to do this")
        return course

    def _get_owned_assignment(self, acting_user, assignment_id):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if assignment is None:
            raise NotFound("Assignment is not found")
        self._get_owned_course(acting_user, assignment["course_id"])
        return assignment
