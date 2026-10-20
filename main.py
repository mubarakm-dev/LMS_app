from src.data.repositories.user_repo import UserRepository
from src.data.repositories.verification_repo import VerificationRepo
from src.data. repositories.course_repo import CourseRepository
from src.domain.errors import ServiceUnavailable
from src.presentation.app import App
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.course_service import CourseService


def build():
    user_repo = UserRepository()
    verification_repo = VerificationRepo()
    course_repo = CourseRepository()
    auth_service = AuthService(user_repo, verification_repo)
    user_service = UserService(user_repo)
    course_service = CourseService(course_repo)

    return App(auth_service, user_service, course_service)


if __name__ == "__main__":
    try:
        build().main_menu()
    except ServiceUnavailable as e:
        print(f"Startup failed: {e}")
    except KeyboardInterrupt:
        print("\nGoodbye.")
