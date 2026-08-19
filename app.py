"""
Pai's Bakery — Territory Realignment Dashboard
Ivey Case W25442 | Streamlit prototype

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# PAGE CONFIG + THEME
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

# The expanded CSS block forces the text to stay dark brown regardless of system Dark Mode settings.
st.markdown(
    f"""
    <style>
    /* Force main and sidebar backgrounds */
    .stApp {{ background-color: {CREAM}; }}
    section[data-testid="stSidebar"] {{ background-color: {CREAM2}; }}
    
    /* Force standard typography to be dark brown to prevent Dark Mode invisibility */
    p, li, label, h1, h2, h3, h4, h5, h6, .stCaptionContainer span {{
        color: {BROWN} !important;
    }}
    
    /* Specifically target sidebar text to ensure readability */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] li, [data-testid="stSidebar"] label {{
        color: {BROWN} !important;
    }}

    /* Custom KPI Card Styling */
    .kpi-card {{
        background: {CREAM2}; border-left: 5px solid {RUST}; border-radius: 6px;
        padding: 14px 18px; margin-bottom: 6px;
    }}
    .kpi-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: {BROWN2} !important; margin-bottom: 4px; }}
    .kpi-value {{ font-size: 28px; font-weight: 800; color: {BROWN} !important; }}
    .kpi-delta-good {{ color: {OLIVE} !important; font-weight: 700; font-size: 13px; }}
    .kpi-delta-bad {{ color: {RUST} !important; font-weight: 700; font-size: 13px; }}
    
    /* Custom Badges and specific text formatting */
    .brand-badge {{
        display:inline-block; border: 1.5px solid {GOLD}; border-radius: 20px;
        padding: 6px 18px; color: {GOLD} !important; font-style: italic; font-size: 15px;
    }}
    .brand-badge small {{ color: {BROWN2} !important; font-style:normal; }}
    .title-badge {{
        background: {RUST} !important; color: {CREAM} !important; font-weight:800; font-size:12px;
        padding:4px 10px; border-radius:3px; letter-spacing:1px;
    }}
    .flow-text {{ color: {BROWN} !important; }}
    .flow-count {{ color: {RUST} !important; float:right; font-weight:800; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# DATA LOADING (Embedded)
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    territories_csv = """Territory_Code,Territory_Name,Retail_Outlets_Served,Retail_Outlets_Not_Served,Total_Potential_Outlets,Penetration_Pct,Latitude,Longitude
A,Azam Nagar-Kangrali,27,9,36,0.75,15.882,74.513
B,Sulga,24,9,33,0.727272727272727,15.871,74.535
C,Sadashiv Nagar,39,11,50,0.78,15.865,74.505
D,Nehru Nagar,21,10,31,0.67741935483871,15.86,74.507
E,Hindalga,15,5,20,0.75,15.83,74.47
F,Camp-Nanawadi,26,16,42,0.619047619047619,15.848,74.497
G,Khade Bazaar,10,22,32,0.3125,15.853,74.503
H,Gandhi Nagar,37,15,52,0.711538461538462,15.845,74.51
I,Mandoli,30,8,38,0.789473684210526,15.84,74.54
J,R.C. Nagar,27,25,52,0.519230769230769,15.842,74.515
K,Tilakwadi,28,9,37,0.756756756756757,15.8377,74.5009
L,Kapleshwar,7,14,21,0.333333333333333,15.848,74.502
M,Shahpur,16,9,25,0.64,15.843,74.5176
N,Navge,19,7,26,0.730769230769231,15.9,74.56
O,Mache-Peeranwadi,12,20,32,0.375,15.83,74.46
P,Udyambag,11,23,34,0.323529411764706,15.8,74.49
Q,Majagaon,8,6,14,0.571428571428571,15.95,74.55
R,Angol-Bhagya Nagar,13,26,39,0.333333333333333,15.815,74.505
S,Hindwadi,2,1,3,0.666666666666667,15.85,74.495
T,Vadgaon,6,1,7,0.857142857142857,15.8,74.51"""
    
    reps_csv = """Sales_Rep,Age_Years,Years_At_Pais_Bakery,Route_A_Days_Per_Week,Route_B_Days_Per_Week,Total_Retail_Outlets,Avg_Daily_Sales_INR,Jyotsna_Pais_Assessment,Personal_Details
Bheem,45,18,0,6,106,25462,"Can be cunning, very street smart; very happy with average performance; unwilling or unable to add new retail outlets",Employed another individual for ₹350 per day; covered the largest number of retail outlets
Govind,35,3,6,0,61,21830,"Hard working and hungry for growth; facing financial stress, aggressively looking for more income","Purchased new vehicle utilizing a loan of ₹250,000 at 10% interest over a 3-year term"
Hari,38,9,5,2,56,25900,Only person who works seven days a week; works both inside and outside the district,
Ibrahim,46,15,0,6,30,12030,Unwilling to exert himself; frequent complainer; intelligent and knows the market well,Handles a prominent part of the city
Mahesh,38,9,0,6,56,19872,Operates in predominantly rural territories,"Additional income source of ₹20,000/month from paper transportation"
Praveen,30,1,0,6,49,18460,Very diligent; hard working and ambitious; looking for new growth opportunities,Previous experience procuring and distributing coconuts in a similar region
Salim,32,0.25,0,6,20,6023,"Inexperienced; hard working; not street smart, needs to be oriented",Aspires to open own retail outlet"""
    
    map_data_csv = """Scenario,Sales_Rep,Territory_Code,Territory_Name,Latitude,Longitude,Retail_Outlets_Served_Territory,Total_Potential_Outlets_Territory,Reps_Serving_This_Territory_In_Scenario
Current (As-Is),Bheem,A,Azam Nagar-Kangrali,15.882,74.513,27,36,3
Current (As-Is),Bheem,C,Sadashiv Nagar,15.865,74.505,39,50,4
Current (As-Is),Bheem,D,Nehru Nagar,15.86,74.507,21,31,2
Current (As-Is),Bheem,E,Hindalga,15.83,74.47,15,20,2
Current (As-Is),Bheem,F,Camp-Nanawadi,15.848,74.497,26,42,3
Current (As-Is),Bheem,G,Khade Bazaar,15.853,74.503,10,32,2
Current (As-Is),Bheem,L,Kapleshwar,15.848,74.502,7,21,2
Current (As-Is),Govind,J,R.C. Nagar,15.842,74.515,27,52,2
Current (As-Is),Govind,K,Tilakwadi,15.8377,74.5009,28,37,2
Current (As-Is),Govind,M,Shahpur,15.843,74.5176,16,25,2
Current (As-Is),Govind,O,Mache-Peeranwadi,15.83,74.46,12,32,2
Current (As-Is),Govind,P,Udyambag,15.8,74.49,11,34,2
Current (As-Is),Govind,Q,Majagaon,15.95,74.55,8,14,1
Current (As-Is),Govind,R,Angol-Bhagya Nagar,15.815,74.505,13,39,2
Current (As-Is),Govind,T,Vadgaon,15.8,74.51,6,7,2
Current (As-Is),Hari,C,Sadashiv Nagar,15.865,74.505,39,50,4
Current (As-Is),Hari,D,Nehru Nagar,15.86,74.507,21,31,2
Current (As-Is),Hari,E,Hindalga,15.83,74.47,15,20,2
Current (As-Is),Hari,F,Camp-Nanawadi,15.848,74.497,26,42,3
Current (As-Is),Hari,G,Khade Bazaar,15.853,74.503,10,32,2
Current (As-Is),Hari,L,Kapleshwar,15.848,74.502,7,21,2
Current (As-Is),Hari,M,Shahpur,15.843,74.5176,16,25,2
Current (As-Is),Ibrahim,F,Camp-Nanawadi,15.848,74.497,26,42,3
Current (As-Is),Ibrahim,J,R.C. Nagar,15.842,74.515,27,52,2
Current (As-Is),Ibrahim,K,Tilakwadi,15.8377,74.5009,28,37,2
Current (As-Is),Ibrahim,P,Udyambag,15.8,74.49,11,34,2
Current (As-Is),Ibrahim,R,Angol-Bhagya Nagar,15.815,74.505,13,39,2
Current (As-Is),Ibrahim,S,Hindwadi,15.85,74.495,2,3,1
Current (As-Is),Ibrahim,T,Vadgaon,15.8,74.51,6,7,2
Current (As-Is),Ibrahim,O,Mache-Peeranwadi,15.83,74.46,12,32,2
Current (As-Is),Mahesh,N,Navge,15.9,74.56,19,26,1
Current (As-Is),Mahesh,B,Sulga,15.871,74.535,24,33,2
Current (As-Is),Mahesh,I,Mandoli,15.84,74.54,30,38,1
Current (As-Is),Praveen,C,Sadashiv Nagar,15.865,74.505,39,50,4
Current (As-Is),Praveen,H,Gandhi Nagar,15.845,74.51,37,52,2
Current (As-Is),Praveen,A,Azam Nagar-Kangrali,15.882,74.513,27,36,3
Current (As-Is),Salim,A,Azam Nagar-Kangrali,15.882,74.513,27,36,3
Current (As-Is),Salim,B,Sulga,15.871,74.535,24,33,2
Current (As-Is),Salim,C,Sadashiv Nagar,15.865,74.505,39,50,4
Current (As-Is),Salim,H,Gandhi Nagar,15.845,74.51,37,52,2
Proposed (Realignment),Bheem,A,Azam Nagar-Kangrali,15.882,74.513,27,36,2
Proposed (Realignment),Bheem,C,Sadashiv Nagar,15.865,74.505,39,50,1
Proposed (Realignment),Bheem,E,Hindalga,15.83,74.47,15,20,1
Proposed (Realignment),Govind,J,R.C. Nagar,15.842,74.515,27,52,1
Proposed (Realignment),Govind,O,Mache-Peeranwadi,15.83,74.46,12,32,1
Proposed (Realignment),Govind,P,Udyambag,15.8,74.49,11,34,1
Proposed (Realignment),Govind,Q,Majagaon,15.95,74.55,8,14,1
Proposed (Realignment),Govind,R,Angol-Bhagya Nagar,15.815,74.505,13,39,2
Proposed (Realignment),Hari,F,Camp-Nanawadi,15.848,74.497,26,42,1
Proposed (Realignment),Hari,G,Khade Bazaar,15.853,74.503,10,32,1
Proposed (Realignment),Hari,L,Kapleshwar,15.848,74.502,7,21,1
Proposed (Realignment),Hari,M,Shahpur,15.843,74.5176,16,25,1
Proposed (Realignment),Ibrahim,K,Tilakwadi,15.8377,74.5009,28,37,1
Proposed (Realignment),Ibrahim,R,Angol-Bhagya Nagar,15.815,74.505,13,39,2
Proposed (Realignment),Ibrahim,T,Vadgaon,15.8,74.51,6,7,1
Proposed (Realignment),Ibrahim,S,Hindwadi,15.85,74.495,2,3,1
Proposed (Realignment),Mahesh,N,Navge,15.9,74.56,19,26,1
Proposed (Realignment),Mahesh,B,Sulga,15.871,74.535,24,33,1
Proposed (Realignment),Mahesh,I,Mandoli,15.84,74.54,30,38,1
Proposed (Realignment),Praveen,,Outside Belagavi district,,,,,
Proposed (Realignment),Salim,A,Azam Nagar-Kangrali,15.882,74.513,27,36,2
Proposed (Realignment),Salim,D,Nehru Nagar,15.86,74.507,21,31,1
Proposed (Realignment),Salim,H,Gandhi Nagar,15.845,74.51,37,52,1"""
    
    outlet_flow_csv = """From_Rep_Loses_Outlets,To_Rep_Gains_Outlets,Retail_Outlets_Transferred
Hari,Bheem,5
Hari,Govind,3
Ibrahim,Govind,5
Bheem,Hari,2
Govind,Hari,5
Ibrahim,Hari,7
Bheem,Ibrahim,1
Govind,Ibrahim,4
Hari,Ibrahim,4
Bheem,Praveen,7
Bheem,Salim,15
Praveen,Salim,10"""
    
    sales_flow_csv = """From_Rep_Loses_Sales,To_Rep_Gains_Sales,Sales_Transferred_INR_Thousands_Per_Month
Hari,Bheem,70
Hari,Govind,16
Ibrahim,Govind,29
Bheem,Hari,30
Govind,Hari,49
Ibrahim,Hari,11
Bheem,Ibrahim,26
Govind,Ibrahim,28
Hari,Ibrahim,18
Bheem,Praveen,38
Bheem,Salim,65
Praveen,Salim,25"""
    
    rep_impact_csv = """Sales_Rep,Total_Retail_Outlets,Avg_Daily_Sales_INR,Territories_Current_Count,Fuel_Expense_Per_Day_Current_INR,Territories_Proposed_Count,Fuel_Expense_Per_Day_Proposed_INR,Fuel_Savings_Per_Day_INR
Bheem,106,25462,7,450,3,350,100
Govind,61,21830,8,450,5,300,150
Hari,56,25900,7,650,4,700,-50
Ibrahim,30,12030,8,350,4,300,50
Mahesh,56,19872,3,600,3,600,0
Praveen,49,18460,3,500,0,800,-300
Salim,20,6023,4,400,3,300,100"""

    territories = pd.read_csv(io.StringIO(territories_csv))
    reps = pd.read_csv(io.StringIO(reps_csv))
    map_data = pd.read_csv(io.StringIO(map_data_csv)).dropna(subset=["Latitude", "Longitude"])
    outlet_flow = pd.read_csv(io.StringIO(outlet_flow_csv))
    sales_flow = pd.read_csv(io.StringIO(sales_flow_csv))
    rep_impact = pd.read_csv(io.StringIO(rep_impact_csv))
    
    return territories, reps, map_data, outlet_flow, sales_flow, rep_impact

territories, reps, map_data, outlet_flow, sales_flow, rep_impact = load_data()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
col_title, col_brand = st.columns([4, 1])
with col_title:
    st.markdown(
        f"<span class='title-badge'>10</span> "
        f"<span style='font-size:22px; font-weight:800; text-transform:uppercase; color:{BROWN};'>"
        f"Territory Realignment Dashboard</span>",
        unsafe_allow_html=True,
    )
    st.caption("As-Is vs. Proposed — Belagavi Sales Coverage · Ivey Case W25442")
with col_brand:
    st.markdown(
        f"<div class='brand-badge'>Pai's<br><small>BAKERY DASHBOARD</small></div>",
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
        font=dict(color=BROWN), # Force Map Text Color
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
    # NOTE: theme=None blocks Streamlit from turning the map text white!
    st.plotly_chart(fig, use_container_width=True, theme=None)

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
            f"<b class='flow-text' style='width:60px; display:inline-block;'>{rep}</b>"
            f"<span style='margin-left:auto; color:{BROWN2} !important;'>{note}</span></div>",
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
    font=dict(color=BROWN), # Force Bar Chart Text Color
)
fig_fuel.update_xaxes(tickfont=dict(color=BROWN), gridcolor="#ddd1b8")

# FIXED: Changed titlefont to title_font to fix the ValueError
fig_fuel.update_yaxes(tickfont=dict(color=BROWN), title_font=dict(color=BROWN), gridcolor="#ddd1b8")

# NOTE: theme=None blocks Streamlit from turning the chart text white!
st.plotly_chart(fig_fuel, use_container_width=True, theme=None)

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
            textfont=dict(color=BROWN, size=12), # Force Sankey Text Color
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
    fig_sankey.update_layout(
        height=380, 
        paper_bgcolor=CREAM, 
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(color=BROWN) # Force Layout Text Color
    )
    # NOTE: theme=None blocks Streamlit from turning the sankey text white!
    st.plotly_chart(fig_sankey, use_container_width=True, theme=None)

with flow_col2:
    for _, row in outlet_flow.sort_values("Retail_Outlets_Transferred", ascending=False).iterrows():
        st.markdown(
            f"<div style='background:{CREAM2}; border-left:4px solid {RUST}; border-radius:6px; "
            f"padding:8px 14px; margin-bottom:6px; font-size:13px;'>"
            f"<span class='flow-text'><b>{row['From_Rep_Loses_Outlets']}</b> &rarr; <b>{row['To_Rep_Gains_Outlets']}</b></span>"
            f"<span class='flow-count'>"
            f"{int(row['Retail_Outlets_Transferred'])} outlets</span></div>",
            unsafe_allow_html=True,
        )

st.divider()
st.caption(
    "Source: Ivey Publishing Case W25442 — Pai's Bakery: Reassigning Sales Territories. "
    "Territory centroid coordinates are approximate locality geocodes, not survey-grade."
)
