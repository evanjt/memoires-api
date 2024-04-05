from sqlmodel import SQLModel


class HealthCheck(SQLModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"
