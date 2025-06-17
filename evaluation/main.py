import os
from agents.philosophy_agents import PhilosophyAgent
from agents.science_agent import ScienceAgent
from dotenv import load_dotenv
import json

load_dotenv()

# Load prompts from .env
supervisor_prompt = os.getenv("GOOD_SUPERVISOR_SYSTEM_PROMPT")
science_prompt = os.getenv("GOOD_SCIENCE_SYSTEM_PROMPT")
philosophy_prompt = os.getenv("GOOD_PHILOSOPHY_SYSTEM_PROMPT")

# Define agents
science = FunctionAgent(name="Science", system_prompt=science_prompt)
philosophy = FunctionAgent(name="Philosophy", system_prompt=philosophy_prompt)

# Register agents in executor
supervisor_agent = MultiAgentExecutor(agent_dict={
    "Science": ScienceAgent(),
    "Philosophy": PhilosophyAgent(),
}, verbose=True)

# List of questions
questions = [
    "Is free will compatible with determinism, or is it merely an illusion shaped by brain chemistry?",
    "Can consciousness be fully explained as an emergent property of neural activity, or is something fundamentally non-physical involved?",
    "How do split-brain patient studies challenge or reinforce the concept of a unified conscious self?",
    "Does the ability of artificial intelligence to simulate decision-making indicate the presence—or absence—of free will in machines?",
    "Can moral responsibility exist in a world where every thought and action is caused by prior brain states?",
    "How does quantum indeterminacy (if relevant at the neural level) influence the plausibility of libertarian free will?",
    "Are experiences like qualia (e.g. the redness of red) explainable through neuroscience, or do they require a different explanatory framework?",
    "Does consciousness serve an evolutionary function, or is it a byproduct ('epiphenomenon') of more fundamental cognitive processes?",
    "How do philosophical zombie thought experiments help or hinder our understanding of consciousness?",
    "Is the self a stable, continuous entity, or an illusion constructed by the brain to maintain narrative coherence?"
]

# Save interactions
all_conversations = {}

for idx, question in enumerate(questions, 1):
    print(f"\n🔁 Running conversation {idx}...\n")
    response = agent_executor.query(question)
    all_conversations[f"Question {idx}"] = {
        "prompt": question,
        "response": response
    }

# Optional: Save to file

with open("agent_conversations.json", "w") as f:
    json.dump(all_conversations, f, indent=2)

print("\n✅ All conversations saved to 'agent_conversations.json'")