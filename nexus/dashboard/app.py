from __future__ import annotations

import asyncio

import streamlit as st

from nexus.core.config import settings
from nexus.core.orchestrator import OrchestratorAgent
from nexus.dashboard.components.agent_log import render_agent_log
from nexus.dashboard.components.cost_meter import render_cost_meter
from nexus.dashboard.components.memory_viewer import render_memory
from nexus.dashboard.components.task_tree import render_task_tree

st.set_page_config(page_title="NEXUS Dashboard", layout="wide")
st.title("NEXUS — Neural EXecution and Understanding System")

goal = st.text_area("Enter goal", "Build a todo app and test it")

if st.button("Run"):
    orchestrator = OrchestratorAgent(settings)
    output = asyncio.run(orchestrator.run(goal))
    render_task_tree({"tasks": [{"title": "Plan+Execute", "agent_type": "orchestrator"}]})
    render_agent_log([])
    render_memory([])
    render_cost_meter(0.0, settings.session_cost_budget_usd)
    st.success(f"Run finished with status={output['status']}")
    st.json(output)
