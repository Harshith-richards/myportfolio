from __future__ import annotations

import streamlit as st


def render_task_tree(task_tree: dict) -> None:
    st.subheader("Task Tree")
    for task in task_tree.get("tasks", []):
        st.markdown(f"- **{task['title']}** ({task['agent_type']})")
