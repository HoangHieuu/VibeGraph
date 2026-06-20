from app.models.auth_models import SessionView
from app.models.errors import InvalidCredentialsError

DEMO_EMAIL = "builder@vibegraph.dev"
DEMO_PASSWORD = "ship-fast"


def validate_session(email: str, password: str) -> SessionView:
    if email != DEMO_EMAIL or password != DEMO_PASSWORD:
        raise InvalidCredentialsError("Email or password is incorrect.")

    return SessionView(
        user=email,
        token="demo-session-token",
        message="Session validated. Your agent workspace is ready.",
    )
