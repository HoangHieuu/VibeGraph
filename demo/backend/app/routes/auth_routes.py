from fastapi import APIRouter, HTTPException

from app.models.auth_models import LoginRequest, SessionView
from app.models.errors import InvalidCredentialsError
from app.services.session_service import validate_session
from app.tools.activity_tool import record_agent_activity

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=SessionView)
def login(payload: LoginRequest) -> SessionView:
    try:
        session = validate_session(payload.email, payload.password)
    except InvalidCredentialsError as error:
        record_agent_activity("login_rejected", payload.email)
        raise HTTPException(status_code=401, detail=str(error)) from error

    record_agent_activity("login_succeeded", payload.email)
    return session
