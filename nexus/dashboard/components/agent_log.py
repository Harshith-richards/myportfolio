from __future__ import annotations

import streamlit as st


def render_agent_log(events: list[dict]) -> None:
    st.subheader("Execution Log")
    st.json(events)
