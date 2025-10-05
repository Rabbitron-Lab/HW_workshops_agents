import streamlit as st
import os
from typing import List, Dict
from dotenv import load_dotenv

from crew_agent import kickoff_triage

load_dotenv()

st.set_page_config(page_title="Medical Triage Assistant", page_icon="🏥", layout="centered")


def init_state():
	if 'chat_history' not in st.session_state:
		st.session_state.chat_history: List[Dict[str, str]] = []


def header():
	st.markdown("# 🏥 Medical Triage Assistant")
	if not os.getenv("GROQ_API_KEY"):
		st.warning("GROQ_API_KEY is not set. Create a .env file with your key.")


def render_history():
	for msg in st.session_state.chat_history:
		if msg["role"] == "user":
			st.markdown("**👤 You:**")
			st.info(msg["content"])
		else:
			st.markdown("**🏥 Assistant:**")
			st.success(msg["content"])


def main():
	init_state()
	header()

	render_history()
	user_input = st.text_input(
		"Describe your symptoms or ask a question:",
		placeholder="e.g., I have a fever and headache...",
		key="user_input",
	)
	col1, col2 = st.columns([1, 1])
	with col1:
		send = st.button("Send", type="primary")
	with col2:
		if st.button("Clear"):
			st.session_state.chat_history.clear()
			st.rerun()

	if send and user_input.strip():
		st.session_state.chat_history.append({"role": "user", "content": user_input})
		with st.spinner("Analyzing..."):
			try:
				response = kickoff_triage(user_input, st.session_state.chat_history)
				st.session_state.chat_history.append({"role": "assistant", "content": response})
			except Exception as e:
				st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {e}"})
		st.rerun()


if __name__ == "__main__":
	main()
