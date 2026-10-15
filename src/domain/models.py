from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.enums import Role


@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    email: str
    role: Role
    is_verified: bool
    is_active: bool = True
    created_at: Optional[datetime] = None
