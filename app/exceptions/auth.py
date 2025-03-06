from fastapi import (
    HTTPException,
    status,
)


class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )


class InvalidJWTTokenError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {detail}",
        )


class InvalidJWTTokenYypeError(HTTPException):
    def __init__(self, token_type: str, expected: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type {token_type!r}. Expected {expected!r} token.",
        )
