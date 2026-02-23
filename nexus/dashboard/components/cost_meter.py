from __future__ import annotations

import streamlit as st


def render_cost_meter(cost: float, budget: float) -> None:
    st.subheader("Cost Meter")
    st.progress(min(cost / budget, 1.0))
    st.caption(f"${cost:.2f} / ${budget:.2f}")
