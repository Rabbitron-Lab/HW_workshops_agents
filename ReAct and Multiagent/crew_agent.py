import os
from typing import List, Dict
from dotenv import load_dotenv

# CrewAI and LLM
from crewai import Agent, Task, Crew, Process, LLM


load_dotenv()


def _read_system_prompt() -> str:
	with open("react_prompt.txt", "r", encoding="utf-8") as f:
		return f.read().strip()


def _format_memory_from_history(chat_history: List[Dict[str, str]]) -> str:
	# chat_history: list of {"role": "user"|"assistant", "content": str}
	if not chat_history:
		return ""
	pairs: List[str] = []
	# Convert to pairs of User/Assistant; take last 5 exchanges
	temp: List[Dict[str, str]] = chat_history[-10:]  # up to last 5 pairs
	current_user = None
	for msg in temp:
		role = msg.get("role", "")
		content = msg.get("content", "")
		if role == "user":
			current_user = content
		elif role == "assistant" and current_user is not None:
			pairs.append(f"User: {current_user}\nAssistant: {content}")
			current_user = None
	if not pairs:
		return ""
	return "\n\nPrevious Conversation Context (last up to 5):\n" + "\n\n".join(pairs[-5:]) + "\n\n"


def _get_llm() -> LLM:
	api_key = os.getenv("GROQ_API_KEY")
	if not api_key:
		raise ValueError("GROQ_API_KEY environment variable is required")
	# Use the user's requested Groq model
	return LLM(
		model="groq/llama-3.3-70b-versatile",
		api_key=api_key,
	)


def kickoff_triage(user_input: str, chat_history: List[Dict[str, str]] | None = None) -> str:
	"""
	Run the CrewAI medical triage agent with the given user input and optional chat history.
	- user_input: the user's latest message
	- chat_history: list of dicts [{"role": "user"|"assistant", "content": str}], used to build memory
	Returns the structured medical triage response as a string.
	"""
	system_prompt = _read_system_prompt()
	memory_text = _format_memory_from_history(chat_history or [])

	llm = _get_llm()

	agent = Agent(
		role="Virtual Medical Triage Assistant",
		goal="Analyze symptoms and provide safe, structured medical guidance",
		backstory=(
			"You are a specialized virtual medical triage assistant. You analyze symptom patterns, "
			"identify potential conditions from a predefined list, and provide clear, educational guidance. "
			"Always emphasize that outputs are for demo/educational purposes only and not medical advice."
		),
		allow_delegation=False,
		verbose=True,
		llm=llm,
	)

	description = f"""
{system_prompt}

{memory_text}
Current User Input:
{user_input}

Please respond using the exact Output Format and Tone & Style specified in the system prompt.
"""

	task = Task(
		description=description.strip(),
		agent=agent,
		expected_output=(
			"A structured medical triage response that strictly follows the specified Output Format "
			"including Diagnosis Summary, Confirmatory Steps, Treatment Guide, Escalation Flags, "
			"Educational Sidebar, and the required Disclaimer."
		),
	)

	crew = Crew(
		agents=[agent],
		tasks=[task],
		process=Process.sequential,
		verbose=True,
	)

	result = crew.kickoff()
	return str(result).strip()
