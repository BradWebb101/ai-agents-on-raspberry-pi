from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
import time

class SummaryAgent():
    def __init__(self):
        self.name = 'SummaryAgent'
        self.system_prompt = 'You are a summary agent, you send back short and consise summaries no longer than 20 words'
        self.agent = FunctionAgent(
            name=self.name,
            description='You are a summary agent, you send back short and consise summaries',
            llm=Ollama(model="tinyllama", request_timeout=120.0),
            system_prompt=self.system_prompt
        )

    def run(self, user_query, context={}):
        try:
            print('Summary Agent is running')
            response = self.agent.llm.complete(f"{user_query}. Give a summary back no longer than 20 words")
            print('Summary Agent has a response')
            print(response)
            return response
        except Exception as e:
            print(f"[ERROR] ScienceAgent encountered an error: {e}")
            return "Error occurred while processing the query."