from src.domain.enums import Role
from src.integration.csv_writer import write_csv
from src.services.permissions import require_role


class AdminReportService:
    def __init__(self, stats_repo):
        self.stats_repo = stats_repo

    @require_role(Role.ADMIN)
    def get_overview(self, acting_user):
        return self.stats_repo.get_overview()

    @require_role(Role.ADMIN)
    def top_courses(self, acting_user, limit=5):
        return self.stats_repo.top_courses(limit)

    @require_role(Role.ADMIN)
    def export_overview(self, acting_user):
        stats = self.stats_repo.get_overview()
        rows = [(name.replace("_", " ").capitalize(), value) for name, value in stats.items()]
        return write_csv("platform_summary", ["Metric", "Value"], rows)
