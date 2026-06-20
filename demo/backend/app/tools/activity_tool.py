from collections import deque

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["agent-tools"])
_events: deque["ActivityEvent"] = deque(maxlen=8)


class ActivityEvent(BaseModel):
    action: str
    subject: str


def record_agent_activity(action: str, subject: str) -> None:
    _events.appendleft(ActivityEvent(action=action, subject=subject))


@router.get("/agent-activity", response_model=list[ActivityEvent])
def list_agent_activity() -> list[ActivityEvent]:
    return list(_events)
