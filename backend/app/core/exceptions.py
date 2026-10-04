class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__("AUTHENTICATION_REQUIRED", message, 401)


class AuthorizationError(AppError):
    def __init__(self, message: str = "You do not have permission for this action"):
        super().__init__("FORBIDDEN", message, 403)


class ResourceNotFoundError(AppError):
    def __init__(self, resource: str):
        super().__init__("NOT_FOUND", f"{resource} not found", 404)
