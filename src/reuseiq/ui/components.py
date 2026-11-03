"""
ReUseIQ - UI Visual Components

Provides Plotly charts and visual widgets for multi-criteria comparison,
fuzzy membership curves, risk gauges, and action badges.
"""

from typing import Any, Dict, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


ACTION_COLORS = {
    "repair": "#2563EB",              # Blue
    "refurbish": "#7C3AED",           # Purple
    "component_recovery": "#059669",  # Emerald Green
    "donate_reuse": "#D97706",        # Amber
    "recycle": "#DC2626",             # Crimson
    "safety_assessment_required": "#EA580C"  # Orange
}

ACTION_ICONS = {
    "repair": "🔧",
    "refurbish": "✨",
    "component_recovery": "🧩",
    "donate_reuse": "🎁",
    "recycle": "♻️",
    "safety_assessment_required": "⚠️"
}


def render_utility_comparison_chart(all_utilities: Dict[str, Dict[str, float]], feasible_options: List[str]) -> go.Figure:
    """
    Renders a grouped bar chart comparing Economic, Environmental, and Life Extension
    criteria across all 5 candidate actions, highlighting feasible options.
    """
    categories = ["Economic Feasibility", "Environmental Benefit", "Life Extension"]
    actions = list(all_utilities.keys())

    fig = go.Figure()

    for action in actions:
        scores = all_utilities[action]
        is_feasible = action in feasible_options
        label = action.replace("_", " ").title()
        if not is_feasible:
            label += " (Disqualified/Blocked)"

        fig.add_trace(go.Bar(
            name=label,
            x=categories,
            y=[scores["economic"], scores["environmental"], scores["life_extension"]],
            marker_color=ACTION_COLORS.get(action, "#64748B"),
            opacity=1.0 if is_feasible else 0.35,
            text=[f"{scores['economic']}", f"{scores['environmental']}", f"{scores['life_extension']}"],
            textposition="auto"
        ))

    fig.update_layout(
        title="Multi-Criteria Evaluation (0 - 100 Scale)",
        barmode="group",
        yaxis=dict(title="Score", range=[0, 105]),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=50, b=80),
        template="plotly_white"
    )
    return fig


def render_radar_chart(all_utilities: Dict[str, Dict[str, float]], feasible_options: List[str]) -> go.Figure:
    """Renders a radar / spider chart comparing feasible actions across dimensions."""
    categories = ["Economic", "Environmental", "Life Extension"]
    fig = go.Figure()

    for action in feasible_options:
        if action in all_utilities:
            scores = all_utilities[action]
            r_vals = [scores["economic"], scores["environmental"], scores["life_extension"], scores["economic"]]
            fig.add_trace(go.Scatterpolar(
                r=r_vals,
                theta=categories + [categories[0]],
                fill="toself",
                name=action.replace("_", " ").title(),
                line_color=ACTION_COLORS.get(action, "#2563EB")
            ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Feasible Actions Trade-off Profile",
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def render_fuzzy_curve_chart(damage_severity: float, damage_memberships: Dict[str, float]) -> go.Figure:
    """Renders triangular fuzzy membership functions for damage severity."""
    x = [i for i in range(101)]

    # Low: (0, 0, 50)
    def tri(val, a, b, c):
        if val < a or val > c:
            return 0.0
        if a == b:
            return 1.0 if val <= b else (c - val) / (c - b)
        if b == c:
            return 1.0 if val >= b else (val - a) / (b - a)
        if val == b:
            return 1.0
        if val < b:
            return (val - a) / (b - a)
        return (c - val) / (c - b)

    low_y = [tri(v, 0, 0, 50) for v in x]
    med_y = [tri(v, 0, 50, 100) for v in x]
    high_y = [tri(v, 50, 100, 100) for v in x]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=low_y, mode="lines", name="Low Damage", line=dict(color="#10B981", width=2)))
    fig.add_trace(go.Scatter(x=x, y=med_y, mode="lines", name="Moderate Damage", line=dict(color="#F59E0B", width=2)))
    fig.add_trace(go.Scatter(x=x, y=high_y, mode="lines", name="High Damage", line=dict(color="#EF4444", width=2)))

    # Vertical line at current device damage
    fig.add_vline(
        x=damage_severity,
        line_dash="dash",
        line_color="#1E293B",
        annotation_text=f"Device Damage: {damage_severity:.0f}",
        annotation_position="top right"
    )

    fig.update_layout(
        title="Fuzzy Sets: Damage Severity Membership Curves",
        xaxis_title="Damage Severity (0-100)",
        yaxis_title="Degree of Membership (μ)",
        yaxis=dict(range=[-0.05, 1.1]),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig


def render_action_distribution_chart(by_action: Dict[str, int]) -> go.Figure:
    """Renders a donut chart of decisions across the device inventory."""
    if not by_action:
        return go.Figure()

    labels = [k.replace("_", " ").title() for k in by_action.keys()]
    values = list(by_action.values())
    colors = [ACTION_COLORS.get(k, "#64748B") for k in by_action.keys()]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=colors),
        textinfo="label+percent+value"
    )])
    fig.update_layout(
        title="Inventory Distribution by Recommended Action",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
