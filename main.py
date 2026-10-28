from src.data.repositories.course_repo import CourseRepository
from src.data.repositories.enrollment_repo import EnrollmentRepository
from src.data.repositories.user_repo import UserRepository
from src.data.repositories.verification_repo import VerificationRepo
from src.data.repositories.lesson_repo import LessonRepository
from src.data.repositories.assignment_repo import AssignmentRepository
from src.data.repositories.submission_repo import SubmissionRepository
from src.data.repositories.quiz_repo import QuizRepository
from src.data.repositories.question_repo import QuestionRepository
from src.data.repositories.result_repo import ResultRepository
from src.data.repositories.stats_repo import StatsRepository
from src.data.repositories.report_repo import ReportRepository

from src.domain.errors import ServiceUnavailable
from src.presentation.app import App
from src.services.auth_service import AuthService
from src.services.course_service import CourseService
from src.services.enrollment_service import EnrollmentService
from src.services.user_service import UserService
from src.services.lesson_service import LessonService
from src.services.assignment_service import AssignmentService
from src.services.quiz_service import QuizService
from src.services.admin_report_service import AdminReportService
from src.services.teacher_report_service import TeacherReportService





def build():
    user_repo = UserRepository()
    verification_repo = VerificationRepo()
    course_repo = CourseRepository()
    enrollment_repo = EnrollmentRepository()
    lesson_repo = LessonRepository()
    submission_repo = SubmissionRepository()
    assignment_repo = AssignmentRepository()
    quiz_repo = QuizRepository()
    question_repo = QuestionRepository()
    result_repo = ResultRepository()
    stats_repo = StatsRepository()
    report_repo = ReportRepository()

    auth_service = AuthService(user_repo, verification_repo)
    user_service = UserService(user_repo)
    course_service = CourseService(course_repo, enrollment_repo)
    enrollment_service = EnrollmentService(enrollment_repo, course_repo)
    lesson_service = LessonService(lesson_repo, course_repo, enrollment_repo)
    assignment_service = AssignmentService(assignment_repo, submission_repo, course_repo, enrollment_repo)
    quiz_service = QuizService(quiz_repo, question_repo, result_repo, course_repo, enrollment_repo)

    admin_report_service = AdminReportService(stats_repo)
    teacher_report_service = TeacherReportService(
        report_repo,
        result_repo,
        submission_repo,
        quiz_repo,
        assignment_repo,
        course_repo,
        enrollment_repo,
    )

    return App(
        auth_service,
        user_service,
        course_service,
        enrollment_service,
        lesson_service,
        assignment_service,
        quiz_service,
        admin_report_service,
        teacher_report_service,
    )


if __name__ == "__main__":
    try:
        build().main_menu()
    except ServiceUnavailable as e:
        print(f"Startup failed: {e}")
    except KeyboardInterrupt:
        print("\nGoodbye.")
