from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama

class SummaryAgent():
    def __init__(self):
        self.name = 'SummaryAgent'
        self.system_prompt = 'You are a 5 word summary agent, summarize to 5 words only'
        self.agent = FunctionAgent(
            name=self.name,
            description='You are a summary agent, you send back short and consise summaries',
            llm=Ollama(model="tinyllama"),
            system_prompt=self.system_prompt
        )

    def run(self, user_query, context={}):
        try:
            print(self.agent.system_prompt)
            # Combine user query, database context, and additional context
            response = self.agent.llm.complete(f"{user_query}. ")
            print('Summary')
            print('='*20)
            print(response)
            return response
        except Exception as e:
            print(f"[ERROR] ScienceAgent encountered an error: {e}")
            return "Error occurred while processing the query."