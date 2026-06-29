"""Exception hierarchy for notaires_immo."""


class NotairesError(Exception):
    """Base exception for all notaires_immo errors."""


class ApiBadRequest(NotairesError):
    """The API rejected the request (HTTP 400) — likely invalid parameters."""


class NotFound(NotairesError):
    """The listing was not found (HTTP 404)."""


class RateLimited(NotairesError):
    """The API responded with HTTP 429."""


class ApiSchemaError(NotairesError):
    """The API response does not match the expected schema.

    Raised when a required field is missing from a response. Use this to detect
    upstream API drift and open an `api_drift` issue on the repo.
    """

    def __init__(self, message: str, raw: object = None) -> None:
        super().__init__(message)
        self.raw = raw
