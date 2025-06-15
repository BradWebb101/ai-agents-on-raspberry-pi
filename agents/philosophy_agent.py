from python_a2a import AgentCard, A2AServer, Message, TextContent, MessageRole
from python_a2a.discovery import enable_discovery
from python_a2a.server import run_server
import os

class PhilosophyAgent(A2AServer):
    def __init__(self, url):
        agent_card = AgentCard(
            name="PhilosophyAgent",
            description="A wise and thoughtful philosophy expert.",
            url=url,
            version="1.0.0",
            capabilities={"philosophy": True}
        )
        super().__init__(agent_card=agent_card)

    def handle_message(self, message: Message) -> Message:
        return Message(
            content=TextContent(
                text=f"PhilosophyAgent received: {message.content.text}"
            ),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

if __name__ == "__main__":
    registry_url = os.environ.get("A2A_REGISTRY_URL", "http://localhost:8000")
    agent_url = os.environ.get("A2A_AGENT_URL", "http://localhost:8001")
    agent = PhilosophyAgent(url=agent_url)
    enable_discovery(agent, registry_url=registry_url)
    run_server(agent, host="0.0.0.0", port=8001) 