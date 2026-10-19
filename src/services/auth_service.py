import bcrypt

from src.domain.enums import Role
from src.domain.errors import AuthError, DuplicateError, ValidationError
from src.domain.models import User
from src.services import validators


class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def register(self, first_name, last_name, email, password, confirm_password):
        if not first_name.strip() or not last_name.strip():
            raise ValidationError("First and last name are required.")

        email = email.strip().lower()
        if not validators.validate_email(email):
            raise ValidationError("Invalid email format.")

        if not validators.validate_password(password):
            raise ValidationError(
                "Password needs 8+ characters with an uppercase letter, "
                "a lowercase letter, a number and a special character."
            )

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        if self.user_repo.email_exists(email):
            raise DuplicateError("An account with that email already exists.")

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return self.user_repo.create(first_name.strip(), last_name.strip(), email, hashed)

    def login(self, email, password):
        user = self.user_repo.get_by_email(email.strip().lower())

        if user is None or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            raise AuthError("Invalid email or password.")

        if not user["is_active"]:
            raise AuthError("This account is disabled.")

        return User(
            id=user["id"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            role=Role(user["role"]),
            is_verified=bool(user["is_verified"]),
            is_active=bool(user["is_active"]),
            created_at=user["created_at"],
        )
