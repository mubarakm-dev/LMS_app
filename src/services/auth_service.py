import random
import string
from datetime import datetime, timedelta

import bcrypt

from src import config
from src.domain.enums import Role
from src.domain.errors import AuthError, DuplicateError, UnverifiedError, ValidationError
from src.domain.models import User
from src.integration.email_client import send_mail
from src.services import validators


class AuthService:
    def __init__(self, user_repo, verification_repo):
        self.user_repo = user_repo
        self.verification_repo = verification_repo

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

        if not user["is_verified"]:
            raise UnverifiedError("Please verify your email first.")

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

    def send_verification_code(self, email):
        user = self.user_repo.get_by_email(email.strip().lower())

        if user is None:
            raise AuthError("No account found for that email.")
        if user["is_verified"]:
            raise AuthError("This account is already verified.")

        code = "".join(random.choice(string.digits) for i in range(config.OTP_LENGTH))
        expires_at = datetime.now() + timedelta(minutes=config.OTP_TTL_MINUTES)

        self.verification_repo.delete_for_user(user["id"])
        self.verification_repo.save_code(user["id"], code, expires_at)

        send_mail(
            user["email"],
            "SQI LMS email verification",
            f"Your verification code is {code}. It expires in {config.OTP_TTL_MINUTES} minutes.",
        )

    def verify_code(self, email, code):
        user = self.user_repo.get_by_email(email.strip().lower())

        if user is None:
            raise AuthError("Invalid verification code.")
        if user["is_verified"]:
            return

        record = self.verification_repo.get_latest(user["id"])

        if record is None:
            raise AuthError("No verification code found. Please request a new one.")
        if record["attempts"] >= config.OTP_MAX_ATTEMPTS:
            raise AuthError("Too many wrong attempts. Please request a new code.")
        if record["expires_at"] < datetime.now():
            raise AuthError("This code has expired. Please request a new one.")

        if code.strip() != record["code"]:
            self.verification_repo.increment_attempts(record["id"])
            raise AuthError("Invalid verification code.")

        self.user_repo.mark_verified(user["id"])
        self.verification_repo.delete_for_user(user["id"])
