from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsError(HTTPException):
    def __init__(self, detail: str = "Already exists") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
