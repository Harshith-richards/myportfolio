from __future__ import annotations

import streamlit as st


def render_memory(memories: list[dict]) -> None:
    st.subheader("Memory")
    st.json(memories)
