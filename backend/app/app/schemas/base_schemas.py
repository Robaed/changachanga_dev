from datetime import datetime
from typing import Any, Optional

import pydantic
from pydantic import BaseModel


class ApiError(BaseModel):
    status_code: str
    message: str
    inner_error: Optional[Any] = None


class AuditColumnsCreate:
    is_deleted: bool = False
    last_edited_date_utc: datetime = pydantic.Field(default_factory=datetime.utcnow)
    last_edited_by: str = 'SYSTEM'
    created_by: str = 'SYSTEM'
