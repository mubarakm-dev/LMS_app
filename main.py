from src.data.repositories.user_repo import UserRepository
from src.data.repositories.verification_repo import VerificationRepo
from src.domain.errors import ServiceUnavailable
from src.presentation.app import App
from src.services.auth_service import AuthService


def build():
    user_repo = UserRepository()
    verification_repo = VerificationRepo()
    auth_service = AuthService(user_repo, verification_repo)
    return App(auth_service)


if __name__ == "__main__":
    try:
        build().main_menu()
    except ServiceUnavailable as e:
        print(f"Startup failed: {e}")
    except KeyboardInterrupt:
        print("\nGoodbye.")
