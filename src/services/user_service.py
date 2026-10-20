from src.domain.enums import Role
from src.domain.errors import NotFound, PermissionDenied, ValidationError
from src.services.permissions import require_role


class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    @require_role(Role.ADMIN)
    def list_users(self, acting_user):
        return self.user_repo.list_all()

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
