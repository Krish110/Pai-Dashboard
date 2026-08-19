"""
Pai's Bakery — Territory Realignment Dashboard
Ivey Case W25442 | Streamlit prototype

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Data source: Pais_Bakery_Territory_Dashboard_Data.xlsx (exported to /data as CSVs)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# PAGE CONFIG + THEME (matches the "Baking the Boundaries" deck palette)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pai's Bakery — Territory Realignment Dashboard",
    page_icon="🥖",
    layout="wide",
)

CREAM = "#F5EFE3"
CREAM2 = "#EFE7D6"
BROWN = "#2B1B12"
BROWN2 = "#4A3222"
RUST = "#B14A26"
OLIVE = "#4B5A32"
GOLD = "#C7963C"

REP_COLORS = {
    "Bheem": "#B14A26",
    "Govind": "#4B5A32",
    "Hari": "#274661",
    "Ibrahim": "#C7963C",
    "Mahesh": "#7B4B8A",
    "Praveen": "#2E8B87",
    "Salim": "#8A5A2B",
}

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {CREAM}; }}
    h1, h2, h3 {{ color: {BROWN} !important; }}
    .kpi-card {{
        background: {CREAM2}; border-left: 5px solid {RUST}; border-radius: 6px;
        padding: 14px 18px; margin-bottom: 6px;
    }}
    .kpi-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px;
                  color: {BROWN2}; margin-bottom: 4px; }}
    .kpi-value {{ font-size: 28px; font-weight: 800; color: {BROWN}; }}
    .kpi-delta-good {{ color: {OLIVE}; font-weight: 700; font-size: 13px; }}
    .kpi-delta-bad {{ color: {RUST}; font-weight: 700; font-size: 13px; }}
    .brand-badge {{
        display:inline-block; border: 1.5px solid {GOLD}; border-radius: 20px;
        padding: 6px 18px; color: {GOLD}; font-style: italic; font-size: 15px;
    }}
    section[data-testid="stSidebar"] {{ background-color: {CREAM2}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    territories = pd.read_csv("data/territories_master.csv")
    reps = pd.read_csv("data/sales_reps.csv")
    map_data = pd.read_csv("data/map_data.csv").dropna(subset=["Latitude", "Longitude"])
    outlet_flow = pd.read_csv("data/outlet_flow.csv")
    sales_flow = pd.read_csv("data/sales_flow.csv")
    rep_impact = pd.read_csv("data/rep_impact.csv")
    return territories, reps, map_data, outlet_flow, sales_flow, rep_impact

territories, reps, map_data, outlet_flow, sales_flow, rep_impact = load_data()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
col_title, col_brand = st.columns([4, 1])
with col_title:
    st.markdown(
        f"<span style='background:{RUST}; color:{CREAM}; font-weight:800; font-size:12px; "
        f"padding:4px 10px; border-radius:3px; letter-spacing:1px;'>10</span> "
        f"<span style='font-size:22px; font-weight:800; text-transform:uppercase; color:{BROWN};'>"
        f"Territory Realignment Dashboard</span>",
        unsafe_allow_html=True,
    )
    st.caption("As-Is vs. Proposed — Belagavi Sales Coverage · Ivey Case W25442")
with col_brand:
    st.markdown(
        f"<div class='brand-badge'>Pai's<br><small style='color:{BROWN2}; font-style:normal;'>"
        f"BAKERY DASHBOARD</small></div>",
        unsafe_allow_html=True,
    )

st.divider()

# ----------------------------------------------------------------------------
# SCENARIO TOGGLE (sidebar)
# ----------------------------------------------------------------------------
st.sidebar.header("Scenario")
scenario = st.sidebar.radio(
    "Choose plan",
    ["Current (As-Is)", "Proposed (Realignment)"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Reading the map**\n\n"
    "- Circle size = retail outlets served\n"
    "- Color = sales representative\n"
    "- Dashed / bold outline = overlapping coverage (more than 1 rep in that territory)"
)
st.sidebar.markdown("---")
selected_reps = st.sidebar.multiselect(
    "Filter reps", options=list(REP_COLORS.keys()), default=list(REP_COLORS.keys())
)

scenario_df = map_data[(map_data["Scenario"] == scenario) & (map_data["Sales_Rep"].isin(selected_reps))]

# ----------------------------------------------------------------------------
# KPI ROW
# ----------------------------------------------------------------------------
fuel_col_current = "Fuel_Expense_Per_Day_Current_INR"
fuel_col_proposed = "Fuel_Expense_Per_Day_Proposed_INR"
fuel_col = fuel_col_current if scenario == "Current (As-Is)" else fuel_col_proposed
other_fuel_col = fuel_col_proposed if scenario == "Current (As-Is)" else fuel_col_current

total_fuel = rep_impact[fuel_col].sum()
other_fuel = rep_impact[other_fuel_col].sum()
fuel_delta = other_fuel - total_fuel  # positive = current scenario saves vs the other

overlap_count = int((scenario_df["Reps_Serving_This_Territory_In_Scenario"] > 1).sum())
territories_covered = scenario_df["Territory_Code"].nunique()
total_assignments = len(scenario_df)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>Territory-Rep Assignments</div>"
        f"<div class='kpi-value'>{total_assignments}</div></div>",
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>Overlapping Assignments</div>"
        f"<div class='kpi-value'>{overlap_count}</div></div>",
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>Territories Covered</div>"
        f"<div class='kpi-value'>{territories_covered} / 20</div></div>",
        unsafe_allow_html=True,
    )
with k4:
    if scenario == "Current (As-Is)":
        delta_html = ""
    elif fuel_delta > 0:
        delta_html = f"<div class='kpi-delta-good'>▼ ₹{fuel_delta:.0f} saved vs Current</div>"
    elif fuel_delta < 0:
        delta_html = f"<div class='kpi-delta-bad'>▲ ₹{abs(fuel_delta):.0f} more than Current</div>"
    else:
        delta_html = "<div>No change</div>"
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>Fleet Fuel Cost / Day</div>"
        f"<div class='kpi-value'>₹{total_fuel:.0f}</div>{delta_html}</div>",
        unsafe_allow_html=True,
    )

st.write("")

# ----------------------------------------------------------------------------
# MAP
# ----------------------------------------------------------------------------
map_col, side_col = st.columns([3, 1])

with map_col:
    st.subheader("Territory Coverage Map")
    plot_df = scenario_df.copy()
    plot_df["overlap"] = plot_df["Reps_Serving_This_Territory_In_Scenario"] > 1
    plot_df["marker_size"] = plot_df["Retail_Outlets_Served_Territory"].clip(lower=3)

    fig = px.scatter_map(
        plot_df,
        lat="Latitude",
        lon="Longitude",
        color="Sales_Rep",
        size="marker_size",
        size_max=32,
        hover_name="Territory_Name",
        hover_data={
            "Territory_Code": True,
            "Retail_Outlets_Served_Territory": True,
            "Total_Potential_Outlets_Territory": True,
            "Reps_Serving_This_Territory_In_Scenario": True,
            "Latitude": False,
            "Longitude": False,
            "marker_size": False,
        },
        color_discrete_map=REP_COLORS,
        zoom=12,
        center={"lat": 15.855, "lon": 74.505},
        height=520,
    )
    fig.update_layout(
        map_style="carto-positron",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        paper_bgcolor=CREAM,
    )
    # Ring the overlapping territories in rust
    overlap_pts = plot_df[plot_df["overlap"]]
    if not overlap_pts.empty:
        fig.add_trace(
            go.Scattermap(
                lat=overlap_pts["Latitude"],
                lon=overlap_pts["Longitude"],
                mode="markers",
                marker=dict(size=overlap_pts["marker_size"] * 1.15, color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=False,
                marker_symbol=None,
            )
        )
    st.plotly_chart(fig, use_container_width=True)

with side_col:
    st.subheader("Reps & Load")
    load_summary = (
        scenario_df.groupby("Sales_Rep")
        .agg(territories=("Territory_Code", "nunique"))
        .reindex(list(REP_COLORS.keys()))
        .fillna(0)
        .astype(int)
    )
    for rep, row in load_summary.iterrows():
        note = f"{row['territories']} territories"
        if rep == "Praveen" and scenario == "Proposed (Realignment)":
            note = "outside Belagavi"
        st.markdown(
            f"<div style='display:flex; align-items:center; gap:8px; font-size:13px; padding:4px 0; "
            f"border-bottom:1px dotted #ddd1b8;'>"
            f"<span style='width:11px; height:11px; border-radius:50%; background:{REP_COLORS[rep]}; "
            f"display:inline-block;'></span>"
            f"<b style='width:60px; display:inline-block;'>{rep}</b>"
            f"<span style='margin-left:auto; color:{BROWN2};'>{note}</span></div>",
            unsafe_allow_html=True,
        )

st.divider()

# ----------------------------------------------------------------------------
# FUEL COST COMPARISON
# ----------------------------------------------------------------------------
st.subheader("Fuel Cost per Rep — Current vs Proposed")
st.caption(
    "From Exhibit 14 / Rep_Impact_Summary. Net effect: ₹50/day saved fleet-wide — but savings "
    "are uneven. Hari and Praveen see fuel costs **rise** under the proposal."
)

fuel_long = rep_impact.melt(
    id_vars="Sales_Rep",
    value_vars=[fuel_col_current, fuel_col_proposed],
    var_name="Plan",
    value_name="Fuel_INR_per_day",
)
fuel_long["Plan"] = fuel_long["Plan"].map(
    {fuel_col_current: "Current", fuel_col_proposed: "Proposed"}
)
fig_fuel = px.bar(
    fuel_long,
    x="Sales_Rep",
    y="Fuel_INR_per_day",
    color="Plan",
    barmode="group",
    color_discrete_map={"Current": "#B8A98A", "Proposed": RUST},
    height=380,
)
fig_fuel.update_layout(
    plot_bgcolor=CREAM,
    paper_bgcolor=CREAM,
    legend_title_text="",
    xaxis_title="",
    yaxis_title="₹ per day",
)
st.plotly_chart(fig_fuel, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# OUTLET REALLOCATION FLOW
# ----------------------------------------------------------------------------
st.subheader("Retail Outlet Reallocation Flow")
st.caption(
    "Exhibit 12 — who gains/loses accounts under the proposal. This is the friction map "
    "for the 'Sales Team Reaction' discussion."
)

flow_col1, flow_col2 = st.columns([1, 1])

with flow_col1:
    reps_list = sorted(set(outlet_flow["From_Rep_Loses_Outlets"]) | set(outlet_flow["To_Rep_Gains_Outlets"]))
    rep_idx = {r: i for i, r in enumerate(reps_list)}
    fig_sankey = go.Figure(
        go.Sankey(
            node=dict(
                label=reps_list,
                color=[REP_COLORS.get(r, "#999") for r in reps_list],
                pad=20,
                thickness=18,
            ),
            link=dict(
                source=[rep_idx[r] for r in outlet_flow["From_Rep_Loses_Outlets"]],
                target=[rep_idx[r] for r in outlet_flow["To_Rep_Gains_Outlets"]],
                value=outlet_flow["Retail_Outlets_Transferred"],
                color="rgba(177,74,38,0.35)",
            ),
        )
    )
    fig_sankey.update_layout(height=380, paper_bgcolor=CREAM, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_sankey, use_container_width=True)

with flow_col2:
    for _, row in outlet_flow.sort_values("Retail_Outlets_Transferred", ascending=False).iterrows():
        st.markdown(
            f"<div style='background:{CREAM2}; border-left:4px solid {RUST}; border-radius:6px; "
            f"padding:8px 14px; margin-bottom:6px; font-size:13px;'>"
            f"<b>{row['From_Rep_Loses_Outlets']}</b> &rarr; <b>{row['To_Rep_Gains_Outlets']}</b>"
            f"<span style='float:right; font-weight:800; color:{RUST};'>"
            f"{int(row['Retail_Outlets_Transferred'])} outlets</span></div>",
            unsafe_allow_html=True,
        )

st.divider()
st.caption(
    "Source: Ivey Publishing Case W25442 — Pai's Bakery: Reassigning Sales Territories. "
    "Territory centroid coordinates are approximate locality geocodes, not survey-grade."
)
