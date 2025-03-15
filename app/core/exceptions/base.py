class BaseAppException(Exception):
    status_code: int
    detail: str

    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code

    def __str__(self):
        return str(self.detail)
