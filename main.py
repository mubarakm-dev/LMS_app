from src.data.repositories.course_repo import CourseRepository
from src.data.repositories.enrollment_repo import EnrollmentRepository
from src.data.repositories.user_repo import UserRepository
from src.data.repositories.verification_repo import VerificationRepo
from src.domain.errors import ServiceUnavailable
from src.presentation.app import App
from src.services.auth_service import AuthService
from src.services.course_service import CourseService
from src.services.enrollment_service import EnrollmentService
from src.services.user_service import UserService


def build():
    user_repo = UserRepository()
    verification_repo = VerificationRepo()
    course_repo = CourseRepository()
    enrollment_repo = EnrollmentRepository()

    auth_service = AuthService(user_repo, verification_repo)
    user_service = UserService(user_repo)
    course_service = CourseService(course_repo, enrollment_repo)
    enrollment_service = EnrollmentService(enrollment_repo, course_repo)

    return App(auth_service, user_service, course_service, enrollment_service)


if __name__ == "__main__":
    try:
        build().main_menu()
    except ServiceUnavailable as e:
        print(f"Startup failed: {e}")
    except KeyboardInterrupt:
        print("\nGoodbye.")
