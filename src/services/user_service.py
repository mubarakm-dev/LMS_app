import bcrypt

from src.domain.enums import Role
from src.domain.errors import AuthError, NotFound, PermissionDenied, ValidationError
from src.services import validators
from src.services.permissions import check_account, require_role

ANY_ROLE = (Role.STUDENT, Role.INSTRUCTOR, Role.ADMIN)


class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def check_session(self, acting_user):
        if acting_user is None:
            raise AuthError("You must be logged in.")
        check_account(acting_user, self.user_repo.get_by_id(acting_user.id))

    @require_role(Role.ADMIN)
    def list_users(self, acting_user):
        return self.user_repo.list_all()

    @require_role(Role.ADMIN)
    def search_users(self, acting_user, term="", role=None, active=None):
        if role is not None:
            try:
                role = Role(role).value
            except ValueError:
                raise ValidationError("Invalid role.")

        return self.user_repo.search(term.strip() or None, role, active)

    @require_role(Role.ADMIN)
    def change_role(self, acting_user, target_user_id, new_role):
        try:
            role = Role(new_role)
        except ValueError:
            raise ValidationError("Invalid role.")

        target = self.user_repo.get_by_id(target_user_id)
        if target is None:
            raise NotFound("User not found.")

        if target["id"] == acting_user.id:
            raise PermissionDenied("You cannot change your own role.")

        if target["role"] == role.value:
            raise ValidationError(f"User is already {role.value}.")

        self.user_repo.update_role(target_user_id, role.value)

    @require_role(Role.ADMIN)
    def set_active(self, acting_user, target_user_id, active):
        target = self.user_repo.get_by_id(target_user_id)
        if target is None:
            raise NotFound("User not found.")

        if target["id"] == acting_user.id:
            raise PermissionDenied("You cannot disable your own account.")

        if bool(target["is_active"]) == active:
            raise ValidationError(
                "That account is already active." if active else "That account is already disabled."
            )

        self.user_repo.set_active(target_user_id, active)

    @require_role(*ANY_ROLE)
    def get_profile(self, acting_user):
        profile = self.user_repo.get_by_id(acting_user.id)
        if profile is None:
            raise NotFound("User not found.")
        return profile

    @require_role(*ANY_ROLE)
    def update_profile(self, acting_user, first_name, last_name):
        first_name, last_name = first_name.strip(), last_name.strip()
        if not first_name or not last_name:
            raise ValidationError("First and last name are required.")
        if len(first_name) > 50 or len(last_name) > 50:
            raise ValidationError("Names can be at most 50 characters.")

        self.user_repo.update_name(acting_user.id, first_name, last_name)
        acting_user.first_name = first_name
        acting_user.last_name = last_name

    @require_role(*ANY_ROLE)
    def change_password(self, acting_user, current_password, new_password, confirm_password):
        record = self.user_repo.get_by_email(acting_user.email)
        if record is None or not bcrypt.checkpw(
            current_password.encode(), record["password_hash"].encode()
        ):
            raise AuthError("Your current password is incorrect.")

        if not validators.validate_password(new_password):
            raise ValidationError(
                "Password needs 8+ characters with an uppercase letter, "
                "a lowercase letter, a number and a special character."
            )
        if new_password != confirm_password:
            raise ValidationError("Passwords do not match.")
        if new_password == current_password:
            raise ValidationError("The new password must be different from the current one.")

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        self.user_repo.update_password(acting_user.id, hashed)
