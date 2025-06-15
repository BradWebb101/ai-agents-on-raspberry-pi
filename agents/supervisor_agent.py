from base_agent import BaseAgent
from typing import Dict, Any, List
import asyncio
import logging
import os
from openai import OpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import random
from agents.philosophy_agent import PhilosophyAgentExecutor
from agents.science_agent import ScienceAgentExecutor
from agents.agent_executor import RequestContext, EventQueue
from agents.events import AgentResponseEvent

# Import your agents
from philosophy_agent import PhilosophyAgent
from science_agent import ScienceAgent
from agents.events import (
    Context, LogEvent, QuestionEvent, AgentResponseEvent, DebateStartEvent, DebateEndEvent
)

class AgentSupervisor:
    def __init__(self):
        self.system_prompt = (
            "You are a neutral and fair debate moderator. "
            "You introduce topics, keep the discussion on track, and summarize the key points made by each participant. "
            "You ensure that the debate remains respectful and productive, and you do not take sides."
        )
        self.agents = [PhilosophyAgent(), ScienceAgent()]
        self.logger = logging.getLogger("AgentSupervisor")
        load_dotenv()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.philosophy_collection = "melvis_philosophy"
        self.science_collection = "melvis_science"
        self.context = Context()
        self.philosophy_executor = PhilosophyAgentExecutor()
        self.science_executor = ScienceAgentExecutor()

    async def delegate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a task to the appropriate agent based on the task type.
        """
        task_type = task.get("type", "unknown")
        agent = self.agents.get(task_type)

        if not agent:
            self.logger.error(f"No agent found for task type: {task_type}")
            return {"error": f"No agent found for task type: {task_type}"}

        try:
            result = await agent.process_task(task)
            return result
        except Exception as e:
            self.logger.error(f"Error processing task: {e}")
            return {"error": str(e)}

    async def coordinate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Coordinate multiple tasks, ensuring they are executed in the correct order.
        """
        results = []
        for task in tasks:
            result = await self.delegate_task(task)
            results.append(result)
        return results

    async def handle_error(self, error: Exception, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors that occur during task execution.
        """
        self.logger.error(f"Error handling task: {error}")
        return {"error": str(error), "task": task}

    async def run(self):
        """
        Main loop for the supervisor agent.
        """
        while True:
            # Example: Fetch tasks from a queue or API
            tasks = await self.fetch_tasks()
            results = await self.coordinate_tasks(tasks)
            await self.process_results(results)
            await asyncio.sleep(1)  # Prevent busy-waiting

    async def process_results(self, results: List[Dict[str, Any]]):
        """
        Process the results of the tasks.
        """
        for result in results:
            if "error" in result:
                await self.handle_error(Exception(result["error"]), result.get("task", {}))
            else:
                self.logger.info(f"Task completed successfully: {result}")

    def get_openai_embedding(self, text):
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def query_collection(self, collection_name, question, limit=2):
        query_vector = self.get_openai_embedding(question)
        hits = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [hit.payload.get("text", "") for hit in hits]

    async def run_debate(self, question: str):
        # Start debate event
        start_event = DebateStartEvent(sender="Supervisor", topic=question)
        self.context.add_event(start_event)
        self.context.add_event(LogEvent(sender="Supervisor", msg=f"Debate started on: {question}"))

        # Send question to all agents and gather responses
        question_event = QuestionEvent(sender="Supervisor", question=question)
        responses = []
        for agent in self.agents:
            response_event = await agent.handle_event(question_event, self.context)
            if response_event:
                responses.append(response_event)
                self.context.add_event(LogEvent(sender="Supervisor", msg=f"Received response from {agent.name}"))

        # End debate event
        summary = " | ".join([r.response for r in responses])
        end_event = DebateEndEvent(sender="Supervisor", summary=summary)
        self.context.add_event(end_event)
        self.context.add_event(LogEvent(sender="Supervisor", msg="Debate ended."))

        # Print debate log
        self.print_debate_log()

    def print_debate_log(self):
        print("\n--- Debate Log ---")
        for event in self.context.history:
            if isinstance(event, LogEvent):
                print(f"[{event.timestamp}] {event.sender}: {event.msg}")
            elif isinstance(event, AgentResponseEvent):
                print(f"[{event.timestamp}] {event.agent_name} response: {event.response}")
        print("--- End of Debate ---\n")

    async def run_debate_a2a(self, question: str):
        print("\n--- A2A Protocol Debate ---")
        # Create context and event queues for each agent
        context = RequestContext(user_id="user", metadata={"question": question})
        philosophy_queue = EventQueue()
        science_queue = EventQueue()

        # Run both agents concurrently
        await asyncio.gather(
            self.philosophy_executor.execute(context, philosophy_queue),
            self.science_executor.execute(context, science_queue),
        )

        # Collect responses
        responses = []
        while not philosophy_queue.empty():
            event = await philosophy_queue.dequeue_event()
            if isinstance(event, AgentResponseEvent):
                print(f"PhilosophyAgent: {event.response}")
                responses.append(event)
        while not science_queue.empty():
            event = await science_queue.dequeue_event()
            if isinstance(event, AgentResponseEvent):
                print(f"ScienceAgent: {event.response}")
                responses.append(event)
        print("--- End of A2A Debate ---\n")

if __name__ == "__main__":
    supervisor = AgentSupervisor()
    asyncio.run(supervisor.run()) 