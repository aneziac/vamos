from enum import Enum
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional


class TaskStatus(str, Enum):
    FAILED = 'failed'
    PENDING = 'pending'
    COMPLETE = 'complete'

    def __str__(self) -> str:
        return self.value


@dataclass
class TaskResponse:
    message: str
    transcript: Optional[str] = None


@dataclass
class Task:
    id: UUID
    status: TaskStatus
    timestamp: Optional[datetime] = None
