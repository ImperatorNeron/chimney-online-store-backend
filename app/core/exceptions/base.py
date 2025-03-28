from typing import Optional


class BaseAppException(Exception):
    def __init__(
        self,
        error_code: str,
        detail: str,
        status_code: int,
        meta: Optional[dict] = None,
    ):
        self.error_code = error_code
        self.detail = detail
        self.status_code = status_code
        self.meta = meta or {}
