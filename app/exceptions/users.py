from fastapi import (
    HTTPException,
    status,
)


class UserWasNotFoundError(HTTPException):
    def __init__(self, detail="User wasn`t found."):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class InactiveUserError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive.",
        )


class UserAlreadyExistsError(HTTPException):
    def __init__(self, detail="User already exists."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
