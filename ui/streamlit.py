import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from app.agent import ask

st.set_page_config(page_title="NL2SQL Agent", page_icon="🗃️", layout="wide")
st.title("🗃️ Natural Language to SQL Agent")
st.caption("Ask questions about the company database in plain English.")

# ── Session state for multi-turn conversation ──
if "messages" not in st.session_state:
    st.session_state.messages = []  # chat display
if "llm_history" not in st.session_state:
    st.session_state.llm_history = []  # OpenAI message format for multi-turn

# ── Render chat history ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ── Chat input ──
question = st.chat_input("Ask a question about the database...")

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Call agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = ask(question, st.session_state.llm_history)

        if result["error"]:
            st.error(result["error"])
            if result["sql"]:
                st.code(result["sql"], language="sql")
            response_text = f"❌ {result['error']}"
        else:
            # SQL query
            st.markdown("**Generated SQL:**")
            st.code(result["sql"], language="sql")

            # Explanation
            if result["explanation"]:
                st.info(f"💡 {result['explanation']}")

            # Results table
            data = result["results"]
            if data and data["rows"]:
                df = pd.DataFrame(data["rows"])
                st.dataframe(df, width='stretch')
                st.caption(f"📊 {data['row_count']} row(s) returned in {data['time_ms']} ms")
            else:
                st.warning("Query returned no results.")

            # Follow-up questions as clickable buttons
            if result["follow_ups"]:
                st.markdown("**💬 Follow-up questions:**")
                for fu in result["follow_ups"]:
                    st.markdown(f"- {fu}")

            response_text = f"SQL: `{result['sql']}`\n\n{result['explanation']}"

    # Update histories
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.session_state.llm_history.append({"role": "user", "content": question})
    st.session_state.llm_history.append({"role": "assistant", "content": response_text})