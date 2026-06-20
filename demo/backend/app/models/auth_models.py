from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class SessionView(BaseModel):
    user: str
    token: str
    message: str
