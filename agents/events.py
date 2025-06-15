from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import datetime

# Base Event class
@dataclass
class Event:
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    sender: str = ""
    recipient: Optional[str] = None
    type: str = "event"
    data: Dict[str, Any] = field(default_factory=dict)

# Specific event types
@dataclass
class LogEvent(Event):
    type: str = "log"
    msg: str = ""

@dataclass
class QuestionEvent(Event):
    type: str = "question"
    question: str = ""

@dataclass
class AgentResponseEvent(Event):
    type: str = "response"
    response: str = ""
    agent_name: str = ""

@dataclass
class DebateStartEvent(Event):
    type: str = "debate_start"
    topic: str = ""

@dataclass
class DebateEndEvent(Event):
    type: str = "debate_end"
    summary: str = ""

# Context class for shared state
@dataclass
class Context:
    history: List[Event] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)

    def add_event(self, event: Event):
        self.history.append(event)

    def get_last_event(self, event_type: Optional[str] = None) -> Optional[Event]:
        if event_type:
            for event in reversed(self.history):
                if event.type == event_type:
                    return event
            return None
        return self.history[-1] if self.history else None 