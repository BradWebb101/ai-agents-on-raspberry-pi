from typing import Dict, Any
import logging
from abc import ABC, abstractmethod
from agents.events import Event, Context

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task. Override this method in each agent.
        """
        pass

    async def handle_event(self, event: Event, context: Context):
        raise NotImplementedError("Agents must implement handle_event.") 