from src.domain.enums import Role
from src.domain.errors import NotFound, PermissionDenied, ValidationError
from src.integration.csv_writer import slug, write_csv
from src.services.permissions import require_role


class TeacherReportService:
    def __init__(self, report_repo, result_repo, submission_repo, quiz_repo,
                 assignment_repo, course_repo, enrollment_repo):
        self.report_repo = report_repo
        self.result_repo = result_repo
        self.submission_repo = submission_repo
        self.quiz_repo = quiz_repo
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo

    # views

    @require_role(Role.INSTRUCTOR)
    def course_performance(self, acting_user, course_id):
        self._get_owned_course(acting_user, course_id)
        return self.report_repo.course_performance(course_id)

    @require_role(Role.INSTRUCTOR)
    def student_report(self, acting_user, course_id, student_id):
        self._get_owned_course(acting_user, course_id)

        students = self.enrollment_repo.list_students_for_course(course_id)
        student = next((s for s in students if s["id"] == student_id), None)
        if student is None:
            raise NotFound("That student is not enrolled in this course.")

        return {
            "student": student,
            "quizzes": self.report_repo.student_quiz_results(student_id, course_id),
            "assignments": self.report_repo.student_assignment_marks(student_id, course_id),
        }

    # CSV exports

    @require_role(Role.INSTRUCTOR)
    def export_course_performance(self, acting_user, course_id):
        course = self._get_owned_course(acting_user, course_id)
        rows = self.report_repo.course_performance(course_id)
        if not rows:
            raise ValidationError("No students are enrolled in this course yet.")

        headers = ["Course", "Student ID", "First name", "Last name", "Email",
                   "Quizzes attempted", "Assignments submitted", "Average assignment score"]
        data = [
            (course["title"], r["id"], r["first_name"], r["last_name"], r["email"],
             r["quizzes_attempted"], r["assignments_submitted"], r["avg_assignment_score"])
            for r in rows
        ]
        return write_csv(f"course_{slug(course['title'])}_performance", headers, data)

    @require_role(Role.INSTRUCTOR)
    def export_quiz_results(self, acting_user, quiz_id):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if quiz is None:
            raise NotFound("Quiz is not found")
        course = self._get_owned_course(acting_user, quiz["course_id"])

        rows = self.result_repo.summary_for_quiz(quiz_id)
        if not rows:
            raise ValidationError("There are no attempts to export yet.")

        headers = ["Course", "Quiz", "Student ID", "First name", "Last name", "Email",
                   "Attempts", "Best score", "Average score", "Total marks", "Last attempt"]
        data = [
            (course["title"], quiz["title"], r["user_id"], r["first_name"], r["last_name"],
             r["email"], r["attempts"], r["best_score"], r["average_score"],
             quiz["total_marks"], r["last_attempt"])
            for r in rows
        ]
        return write_csv(f"quiz_{slug(quiz['title'])}_results", headers, data)

    @require_role(Role.INSTRUCTOR)
    def export_assignment_grades(self, acting_user, assignment_id):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if assignment is None:
            raise NotFound("Assignment is not found")
        course = self._get_owned_course(acting_user, assignment["course_id"])

        rows = self.submission_repo.list_for_assignment(assignment_id)
        if not rows:
            raise ValidationError("There are no submissions to export yet.")

        headers = ["Course", "Assignment", "Submission ID", "First name", "Last name", "Email",
                   "Submitted", "Link", "Score", "Max marks", "Feedback", "Released"]
        data = [
            (course["title"], assignment["title"], r["id"], r["first_name"], r["last_name"],
             r["email"], r["submitted_at"], r["submission_link"], r["score"],
             assignment["max_marks"], r["feedback"], "yes" if r["released"] else "no")
            for r in rows
        ]
        return write_csv(f"assignment_{slug(assignment['title'])}_grades", headers, data)

    # helpers

    def _get_owned_course(self, acting_user, course_id):
        course = self.course_repo.get_by_id(course_id)
        if course is None:
            raise NotFound("Course is not found")
        if course["instructor_id"] != acting_user.id:
            raise PermissionDenied("You are not authorized to do this")
        return course
