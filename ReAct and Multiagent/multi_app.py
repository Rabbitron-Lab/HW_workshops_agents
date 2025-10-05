import streamlit as st

from mutliagents import execute


st.set_page_config(page_title="Editorial Crew Chat", page_icon="📝", layout="wide")

st.title("📝 Multiagent Editorial Crew")
st.caption(
    "Chat with a mini editorial team that researches, outlines, writes, fact-checks, and edits technical articles."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(message["content"])  # content is Markdown
        else:
            st.write(message["content"])  # user content as plain text


prompt = st.chat_input("Ask for a technical article topic…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("The crew is working on your article…"):
            try:
                result_md = execute(prompt)
            except Exception as e:
                result_md = f"**Error:** {e}"
        st.markdown(result_md)
    st.session_state.messages.append({"role": "assistant", "content": result_md})


