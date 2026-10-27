from src.domain.enums import Role
from src.services.permissions import require_role


class ReportService:
    def __init__(self, stats_repo):
        self.stats_repo = stats_repo

    @require_role(Role.ADMIN)
    def get_overview(self, acting_user):
        return self.stats_repo.get_overview()

    @require_role(Role.ADMIN)
    def top_courses(self, acting_user, limit=5):
        return self.stats_repo.top_courses(limit)
