import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# GOVERNMENT ROAD SAFETY DECISION SUPPORT SYSTEM
# Intended end user: Government road-safety / transport authorities
# ============================================================

st.set_page_config(
    page_title="Government Road Safety Decision Support System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.main-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.15rem;
}
.subtitle {
    color: #555;
    margin-bottom: 1rem;
}
.priority-high {
    padding: 14px;
    border-radius: 10px;
    border: 2px solid #d32f2f;
    background: #ffebee;
}
.priority-medium {
    padding: 14px;
    border-radius: 10px;
    border: 2px solid #ef8f00;
    background: #fff8e1;
}
.priority-low {
    padding: 14px;
    border-radius: 10px;
    border: 2px solid #2e7d32;
    background: #e8f5e9;
}
.risk-card {
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-bottom: 12px;
}
.small-note {
    font-size: 0.85rem;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


def normalize(series):
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    lo, hi = s.min(), s.max()

    if hi == lo:
        return pd.Series(0.0, index=s.index)

    return (s - lo) / (hi - lo)


def safe_pct(part, total):
    if total in (0, None) or pd.isna(total):
        return 0.0

    return float(part) / float(total) * 100


def time_window(value):
    try:
        hour = int(str(value).strip().split(":")[0])
    except Exception:
        return "Unknown"

    if 5 <= hour < 12:
        return "Morning"

    if 12 <= hour < 17:
        return "Afternoon"

    if 17 <= hour < 22:
        return "Evening"

    return "Night"


def state_alias(state):
    # Align official J&K label with detailed dataset.
    if state == "J & K #":
        return "Jammu and Kashmir"

    return state


# ============================================================
# NEW FEATURE 1
# RISK PRIORITY ENGINE
# ============================================================

def risk_priority_drivers(row, detailed_state):
    """
    Explain why the project gives a state its priority.
    This is transparent analytical reasoning, not ML prediction.
    """

    drivers = []

    # Accident burden
    if row["Accident burden score"] >= 70:
        drivers.append(
            (
                "High accident burden",
                "The state's official 2024 accident count is among the higher values in the comparison set."
            )
        )

    elif row["Accident burden score"] >= 40:
        drivers.append(
            (
                "Moderate accident burden",
                "The state's official 2024 accident burden is in the middle range of the comparison set."
            )
        )

    else:
        drivers.append(
            (
                "Lower accident burden",
                "The state's official 2024 accident burden is below the higher-burden states in the comparison set."
            )
        )

    # Fatality burden
    if row["Fatality burden score"] >= 70:
        drivers.append(
            (
                "High fatality burden",
                "The state's official 2024 fatalities are among the higher values in the comparison set."
            )
        )

    elif row["Fatality burden score"] >= 40:
        drivers.append(
            (
                "Moderate fatality burden",
                "The state's official 2024 fatality burden is in the middle range of the comparison set."
            )
        )

    else:
        drivers.append(
            (
                "Lower fatality burden",
                "The state's official 2024 fatality burden is below the higher-burden states in the comparison set."
            )
        )

    # Recent trend
    if row["2023→2024 %"] > 0:
        drivers.append(
            (
                "Rising recent trend",
                f"Official accidents increased {row['2023→2024 %']:.2f}% from 2023 to 2024."
            )
        )

    else:
        drivers.append(
            (
                "Non-rising recent trend",
                f"Official accidents changed {row['2023→2024 %']:.2f}% from 2023 to 2024."
            )
        )

    # Historical alcohol indicator
    if detailed_state["Alcohol %"] >= 15:
        drivers.append(
            (
                "Elevated alcohol pattern",
                f"Alcohol involvement appears in {detailed_state['Alcohol %']:.1f}% of the detailed records."
            )
        )

    # Historical night indicator
    if detailed_state["Night %"] >= 30:
        drivers.append(
            (
                "Elevated night-time pattern",
                f"{detailed_state['Night %']:.1f}% of the detailed records fall in the project's night-time window."
            )
        )

    return drivers


# ============================================================
# NEW FEATURE 2
# RISK → EVIDENCE → GOVERNMENT ACTION ENGINE
# ============================================================

def intervention_action_cards(row, detailed_state):

    cards = []

    # Rising accidents
    if row["2023→2024 %"] > 5:
        cards.append(
            {
                "Priority": "HIGH",
                "Risk detected": "Rapid increase in official accidents",
                "Evidence": f"{row['2023→2024 %']:.2f}% increase from 2023 to 2024",
                "Government action":
                    "Conduct a district/route-level review to identify locations and factors behind the increase.",
                "Verification":
                    "Validate against local police, transport and engineering records.",
            }
        )

    # Alcohol
    if detailed_state["Alcohol %"] >= 15:
        cards.append(
            {
                "Priority": "HIGH",
                "Risk detected": "Elevated alcohol involvement",
                "Evidence":
                    f"{detailed_state['Alcohol %']:.1f}% of detailed records marked alcohol involvement",
                "Government action":
                    "Consider targeted enforcement, checkpoints and road-safety awareness operations.",
                "Verification":
                    "Compare with local enforcement and impaired-driving records.",
            }
        )

    # Night accidents
    if detailed_state["Night %"] >= 30:
        cards.append(
            {
                "Priority": "HIGH",
                "Risk detected": "High night-time accident share",
                "Evidence":
                    f"{detailed_state['Night %']:.1f}% of detailed records fall in the night window",
                "Government action":
                    "Review road lighting, visibility, signage and night-time enforcement coverage.",
                "Verification":
                    "Perform field engineering and lighting-condition assessment.",
            }
        )

    # Fatality rate
    if row["Fatality rate per 100 accidents"] >= 5:
        cards.append(
            {
                "Priority": "HIGH",
                "Risk detected": "High fatalities relative to accident volume",
                "Evidence":
                    f"{row['Fatality rate per 100 accidents']:.2f} fatalities per 100 official accidents",
                "Government action":
                    "Prioritize road-safety inspection and emergency-response / trauma-care review.",
                "Verification":
                    "Validate with crash severity, response-time and hospital data.",
            }
        )

    # Dominant road type
    if detailed_state["Top road type"] != "Unknown":
        cards.append(
            {
                "Priority": "MEDIUM",
                "Risk detected":
                    f"Dominant road category: {detailed_state['Top road type']}",
                "Evidence":
                    f"Most represented road type in the detailed records: {detailed_state['Top road type']}",
                "Government action":
                    "Review representative roads in this category for engineering and safety deficiencies.",
                "Verification":
                    "Conduct local road-safety inspection before intervention.",
            }
        )

    # Default
    if not cards:
        cards.append(
            {
                "Priority": "ROUTINE",
                "Risk detected": "No project threshold exceeded",
                "Evidence":
                    "Available indicators did not cross the project's intervention thresholds.",
                "Government action":
                    "Continue routine monitoring and investigate emerging local patterns.",
                "Verification":
                    "Reassess using updated official and field-level data.",
            }
        )

    return cards


# ---------- Original intervention helper ----------
def intervention_recommendations(row, detailed_state):

    recs = []

    if row["Alcohol %"] >= 15:
        recs.append(
            (
                "Enforcement",
                "Alcohol involvement is relatively high in the detailed records; "
                "consider targeted enforcement and awareness operations."
            )
        )

    if row["Night %"] >= 30:
        recs.append(
            (
                "Night safety",
                "A substantial share of detailed accidents occurs at night; "
                "assess lighting, visibility and night-time enforcement."
            )
        )

    if row["Fatality rate per 100 accidents"] >= 5:
        recs.append(
            (
                "Road safety & emergency response",
                "Fatality burden is high relative to accident volume; "
                "prioritize road-safety inspection and emergency-response review."
            )
        )

    if row["2023→2024 %"] > 5:
        recs.append(
            (
                "Priority monitoring",
                "Official accident count increased by more than 5% from 2023 to 2024; "
                "investigate the reasons for the increase."
            )
        )

    if detailed_state["Top road type"] != "Unknown":
        recs.append(
            (
                "Infrastructure review",
                f"'{detailed_state['Top road type']}' is the most represented road category "
                "in the detailed records; consider targeted road-safety inspection."
            )
        )

    if not recs:
        recs.append(
            (
                "Routine monitoring",
                "No single indicator crossed the project's intervention thresholds; "
                "continue monitoring and review local patterns."
            )
        )

    return recs
# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    detailed = pd.read_csv(
        "data/accident_prediction_india-1.csv"
    )

    accidents = pd.read_csv(
        "data/road_accidents_2020_2024.csv"
    )

    fatalities = pd.read_csv(
        "data/road_fatalities_2020_2024.csv"
    )

    # Clean official accident data
    for c in accidents.columns:

        if "Accidents" in c or c == "Change from 2023 to 2024":
            accidents[c] = clean_numeric(accidents[c])

    if "% change from 2023 to 2024" in accidents.columns:

        accidents["% change from 2023 to 2024"] = clean_numeric(
            accidents["% change from 2023 to 2024"]
        )

    # Clean official fatality data
    for c in fatalities.columns:

        if "Killed" in c:
            fatalities[c] = clean_numeric(fatalities[c])

    if "% change from 2023 to 2024" in fatalities.columns:

        fatalities["% change from 2023 to 2024"] = clean_numeric(
            fatalities["% change from 2023 to 2024"]
        )

    # Clean detailed dataset
    detailed["Year"] = pd.to_numeric(
        detailed["Year"],
        errors="coerce"
    )

    detailed["Number of Fatalities"] = clean_numeric(
        detailed["Number of Fatalities"]
    )

    detailed["Speed Limit (km/h)"] = clean_numeric(
        detailed["Speed Limit (km/h)"]
    )

    detailed["Time Window"] = detailed[
        "Time of Day"
    ].apply(time_window)

    return detailed, accidents, fatalities


# ============================================================
# LOAD DATA SAFELY
# ============================================================

try:

    df, official_acc, official_fat = load_data()

except Exception as e:

    st.error(
        "The application could not load the datasets."
    )

    st.code(str(e))

    st.info(
        "Check that all three CSV files are inside "
        "the project's data folder."
    )

    st.stop()


# ============================================================
# OFFICIAL STATE-LEVEL PRIORITY TABLE
# ============================================================

acc = official_acc[
    official_acc["State"].notna()
    & (official_acc["State"] != "All India")
].copy()


fat = official_fat[
    official_fat["State"].notna()
    & (official_fat["State"] != "All India")
].copy()


priority = acc[
    [
        "State",
        "2023 Accidents",
        "2024 Accidents",
        "% change from 2023 to 2024",
    ]
].merge(

    fat[
        [
            "State",
            "2023 Killed",
            "2024 Killed"
        ]
    ],

    on="State",
    how="inner",
)


priority = priority.rename(
    columns={
        "% change from 2023 to 2024":
            "2023→2024 %",
    }
)


# ============================================================
# PRIORITY METRICS
# ============================================================

priority[
    "Fatality rate per 100 accidents"
] = (

    priority["2024 Killed"]
    / priority["2024 Accidents"].replace(
        0,
        np.nan
    )
    * 100

).fillna(0)


# Accident burden
priority[
    "Accident burden score"
] = (

    normalize(
        priority["2024 Accidents"]
    )
    * 100

)


# Fatality burden
priority[
    "Fatality burden score"
] = (

    normalize(
        priority["2024 Killed"]
    )
    * 100

)


# Recent trend
trend_for_score = (
    priority["2023→2024 %"]
    .clip(lower=0)
)


priority[
    "Recent trend score"
] = (

    normalize(
        trend_for_score
    )
    * 100

)


# ============================================================
# GOVERNMENT PRIORITY SCORE
# ============================================================

priority[
    "Government Priority Score"
] = (

    0.40
    * priority["Accident burden score"]

    + 0.40
    * priority["Fatality burden score"]

    + 0.20
    * priority["Recent trend score"]

).round(1)


def priority_label(score):

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


priority["Priority"] = (
    priority[
        "Government Priority Score"
    ].apply(priority_label)
)


# ============================================================
# DETAILED HISTORICAL INDICATORS BY STATE
# ============================================================

detail_state = []


for state in priority["State"]:

    dstate = state_alias(state)

    sub = df[
        df["State Name"]
        .astype(str)
        .str.strip()
        == dstate
    ].copy()


    # No detailed records
    if sub.empty:

        detail_state.append(
            {
                "State": state,
                "Detailed records": 0,
                "Alcohol %": 0.0,
                "Night %": 0.0,
                "Fatal detailed %": 0.0,
                "Top road type": "Unknown",
                "Top weather": "Unknown",
            }
        )

        continue


    # Alcohol
    alcohol_yes = (

        sub["Alcohol Involvement"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
        .sum()

    )


    # Night
    night_count = (
        sub["Time Window"]
        == "Night"
    ).sum()


    # Fatal records
    fatal_records = (

        sub["Accident Severity"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("fatal")
        .sum()

    )


    # Dominant road type
    road_mode = (

        sub["Road Type"]
        .dropna()
        .astype(str)
        .str.strip()
        .mode()

    )


    # Dominant weather
    weather_mode = (

        sub["Weather Conditions"]
        .dropna()
        .astype(str)
        .str.strip()
        .mode()

    )


    detail_state.append(
        {
            "State": state,

            "Detailed records":
                len(sub),

            "Alcohol %":
                safe_pct(
                    alcohol_yes,
                    len(sub)
                ),

            "Night %":
                safe_pct(
                    night_count,
                    len(sub)
                ),

            "Fatal detailed %":
                safe_pct(
                    fatal_records,
                    len(sub)
                ),

            "Top road type":
                road_mode.iloc[0]
                if not road_mode.empty
                else "Unknown",

            "Top weather":
                weather_mode.iloc[0]
                if not weather_mode.empty
                else "Unknown",
        }
    )


detail_summary = pd.DataFrame(
    detail_state
)


priority = priority.merge(
    detail_summary,
    on="State",
    how="left"
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🏛️ Government Road Safety Decision Support System'
    '</div>',
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="subtitle">'
    'Analytical console for government road-safety '
    'authorities — priority identification, recent '
    'trend analysis, risk indicators and intervention '
    'planning.'
    '</div>',
    unsafe_allow_html=True,
)


st.warning(
    "Prototype for decision support. The Priority Score "
    "and intervention rules are project-defined analytical "
    "rules, not official government classifications or "
    "automatic policy decisions."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Government Controls"
)


state_options = sorted(
    priority["State"].tolist()
)


selected_state = st.sidebar.selectbox(
    "Select state for detailed review",
    state_options,
)


selected = priority[
    priority["State"]
    == selected_state
].iloc[0]


selected_detail = detail_summary[
    detail_summary["State"]
    == selected_state
].iloc[0]


# ============================================================
# NATIONAL KPIs
# ============================================================

all_acc = official_acc[
    official_acc["State"]
    == "All India"
]


all_fat = official_fat[
    official_fat["State"]
    == "All India"
]


if not all_acc.empty:

    national_acc_2024 = int(
        all_acc.iloc[0]["2024 Accidents"]
    )

else:

    national_acc_2024 = int(
        priority["2024 Accidents"].sum()
    )


if not all_fat.empty:

    national_fat_2024 = int(
        all_fat.iloc[0]["2024 Killed"]
    )

else:

    national_fat_2024 = int(
        priority["2024 Killed"].sum()
    )


high_count = int(
    (
        priority["Priority"]
        == "HIGH"
    ).sum()
)


increasing_count = int(
    (
        priority["2023→2024 %"]
        > 0
    ).sum()
)


k1, k2, k3, k4 = st.columns(4)


k1.metric(
    "Official 2024 accidents",
    f"{national_acc_2024:,}"
)


k2.metric(
    "Official 2024 fatalities",
    f"{national_fat_2024:,}"
)


k3.metric(
    "High-priority states",
    high_count
)


k4.metric(
    "States with rising accidents",
    increasing_count
)


# ============================================================
# MAIN TABS
# ============================================================

tabs = st.tabs(
    [
        "🏛️ Government Overview",
        "🚨 State Priority",
        "🗺️ India Priority Map",
        "📈 2023 → 2024 Trend",
        "🔎 Risk Indicators",
        "📋 Intervention Plan",
    ]
)


# ============================================================
# TAB 1 — GOVERNMENT OVERVIEW
# ============================================================

with tabs[0]:

    st.subheader(
        "Government situation overview"
    )


    col1, col2 = st.columns(2)


    priority_counts = (

        priority["Priority"]
        .value_counts()
        .reindex(
            [
                "HIGH",
                "MEDIUM",
                "LOW"
            ],
            fill_value=0
        )
        .reset_index()

    )


    priority_counts.columns = [
        "Priority",
        "States"
    ]


    fig = px.bar(
        priority_counts,
        x="Priority",
        y="States",
        title=
            "States by government priority category",
        text="States",
    )


    fig.update_traces(
        textposition="outside"
    )


    col1.plotly_chart(
        fig,
        use_container_width=True
    )


    top_states = (

        priority
        .sort_values(
            "Government Priority Score",
            ascending=False
        )
        .head(10)

    )


    fig = px.bar(

        top_states.sort_values(
            "Government Priority Score"
        ),

        x="Government Priority Score",

        y="State",

        orientation="h",

        title=
            "Top 10 states by Government Priority Score",

        text=
            "Government Priority Score",
    )


    fig.update_traces(
        textposition="outside"
    )


    col2.plotly_chart(
        fig,
        use_container_width=True
    )


    st.markdown(
        "### How the priority score is calculated"
    )


    st.write(
        "**Government Priority Score = 40% accident "
        "burden + 40% fatality burden + 20% recent trend.** "
        "Each component is normalized across the states "
        "in the official dataset."
    )


    st.dataframe(

        priority[
            [
                "State",
                "2024 Accidents",
                "2024 Killed",
                "2023→2024 %",
                "Government Priority Score",
                "Priority",
            ]
        ]
        .sort_values(
            "Government Priority Score",
            ascending=False
        ),

        use_container_width=True,

        hide_index=True,
    )


# ============================================================
# TAB 2 — STATE PRIORITY
# ============================================================

with tabs[1]:

    st.subheader(
        f"Government priority assessment — "
        f"{selected_state}"
    )


    p = selected[
        "Government Priority Score"
    ]


    label = selected[
        "Priority"
    ]


    css_class = {

        "HIGH":
            "priority-high",

        "MEDIUM":
            "priority-medium",

        "LOW":
            "priority-low",

    }[label]


    st.markdown(

        f'<div class="{css_class}">'
        f'<h2>Priority: {label}</h2>'

        f'<b>Government Priority Score:</b> '
        f'{p}/100<br>'

        f'<b>2023 → 2024 accident change:</b> '
        f'{selected["2023→2024 %"]:.2f}%'

        f'</div>',

        unsafe_allow_html=True,
    )


    st.write("")


    a, b, c, d = st.columns(4)


    a.metric(
        "2024 accidents",
        f'{int(selected["2024 Accidents"]):,}'
    )


    b.metric(
        "2024 fatalities",
        f'{int(selected["2024 Killed"]):,}'
    )


    c.metric(
        "Fatalities / 100 accidents",
        f'{selected["Fatality rate per 100 accidents"]:.2f}'
    )


    d.metric(
        "Detailed records",
        f'{int(selected_detail["Detailed records"]):,}'
    )


    st.markdown(
        "### Evidence behind the score"
    )


    evidence = pd.DataFrame(
        {
            "Indicator": [
                "Accident burden",
                "Fatality burden",
                "Recent 2023→2024 change",
            ],

            "Value": [
                f'{int(selected["2024 Accidents"]):,} accidents',

                f'{int(selected["2024 Killed"]):,} fatalities',

                f'{selected["2023→2024 %"]:.2f}%',
            ],

            "Score contribution": [

                f'{selected["Accident burden score"]:.1f}/100 × 40%',

                f'{selected["Fatality burden score"]:.1f}/100 × 40%',

                f'{selected["Recent trend score"]:.1f}/100 × 20%',
            ],
        }
    )


    st.dataframe(
        evidence,
        use_container_width=True,
        hide_index=True
    )


    st.caption(
        "The score is an analytical prioritization "
        "mechanism created for this project. It does not "
        "predict an accident or establish causation."
    )
    # ============================================================
# TAB 3 — INDIA PRIORITY MAP
# ============================================================

with tabs[2]:

    st.subheader(
        "India-wide government priority map"
    )

    coords = {

        "Andhra Pradesh": (15.9129, 79.7400),
        "Arunachal Pradesh": (28.2180, 94.7278),
        "Assam": (26.2006, 92.9376),
        "Bihar": (25.0961, 85.3131),
        "Chandigarh": (30.7333, 76.7794),
        "Chhattisgarh": (21.2787, 81.8661),
        "Delhi": (28.7041, 77.1025),
        "Goa": (15.2993, 74.1240),
        "Gujarat": (22.2587, 71.1924),
        "Haryana": (29.0588, 76.0856),
        "Himachal Pradesh": (31.1048, 77.1734),
        "J & K #": (33.7782, 76.5762),
        "Jharkhand": (23.6102, 85.2799),
        "Karnataka": (15.3173, 75.7139),
        "Kerala": (10.8505, 76.2711),
        "Madhya Pradesh": (22.9734, 78.6569),
        "Maharashtra": (19.7515, 75.7139),
        "Manipur": (24.6637, 93.9063),
        "Meghalaya": (25.4670, 91.3662),
        "Mizoram": (23.1645, 92.9376),
        "Nagaland": (26.1584, 94.5624),
        "Odisha": (20.9517, 85.0985),
        "Punjab": (31.1471, 75.3412),
        "Rajasthan": (27.0238, 74.2179),
        "Sikkim": (27.5330, 88.5122),
        "Tamil Nadu": (11.1271, 78.6569),
        "Telangana": (18.1124, 79.0193),
        "Tripura": (23.9408, 91.9882),
        "Uttar Pradesh": (26.8467, 80.9462),
        "Uttarakhand": (30.0668, 79.0193),
        "West Bengal": (22.9868, 87.8550),
        "Andaman & Nicobar Islands": (11.7401, 92.6586),
        "Dadra & Nagar Haveli and Daman & Diu": (20.1809, 73.0169),
        "Ladakh": (34.1526, 77.5771),
        "Lakshadweep": (10.5667, 72.6417),
        "Puducherry": (11.9416, 79.8083),
    }

    map_df = priority.copy()

    map_df["lat"] = map_df["State"].map(
        lambda x: coords.get(
            x,
            (np.nan, np.nan)
        )[0]
    )

    map_df["lon"] = map_df["State"].map(
        lambda x: coords.get(
            x,
            (np.nan, np.nan)
        )[1]
    )

    map_df = map_df.dropna(
        subset=["lat", "lon"]
    )

    fig = px.scatter_geo(

        map_df,

        lat="lat",
        lon="lon",

        size="Government Priority Score",

        color="Priority",

        hover_name="State",

        hover_data={
            "Government Priority Score": True,
            "2024 Accidents": ":,",
            "2024 Killed": ":,",
            "2023→2024 %": ":.2f",
            "lat": False,
            "lon": False,
        },

        projection="mercator",

        scope="asia",

        title=
            "Government intervention priority by state",

        size_max=30,

        category_orders={
            "Priority":
                ["HIGH", "MEDIUM", "LOW"]
        },
    )

    fig.update_geos(

        center={
            "lat": 22.5,
            "lon": 79
        },

        lataxis_range=[
            5,
            38
        ],

        lonaxis_range=[
            65,
            98
        ],

        showcountries=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "Map points represent approximate state/UT "
        "centroids. They are for state-level decision "
        "support and must not be interpreted as GPS-level "
        "accident hotspots."
    )


# ============================================================
# TAB 4 — 2023 → 2024 TREND
# ============================================================

with tabs[3]:

    st.subheader(
        "Official 2023 → 2024 change"
    )

    trend = priority.copy()

    trend["Absolute change"] = (
        trend["2024 Accidents"]
        - trend["2023 Accidents"]
    )

    left, right = st.columns(2)


    # Largest increases
    inc = (
        trend
        .sort_values(
            "Absolute change",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(

        inc.sort_values(
            "Absolute change"
        ),

        x="Absolute change",

        y="State",

        orientation="h",

        title=
            "Largest increases in accident count",

        text="Absolute change",
    )

    fig.update_traces(
        textposition="outside"
    )

    left.plotly_chart(
        fig,
        use_container_width=True,
        key="largest_increases"
    )


    # Largest decreases
    dec = (
        trend
        .sort_values(
            "Absolute change",
            ascending=True
        )
        .head(10)
    )

    fig = px.bar(

        dec.sort_values(
            "Absolute change"
        ),

        x="Absolute change",

        y="State",

        orientation="h",

        title=
            "Largest decreases in accident count",

        text="Absolute change",
    )

    fig.update_traces(
        textposition="outside"
    )

    right.plotly_chart(
        fig,
        use_container_width=True,
        key="largest_decreases"
    )


    st.dataframe(

        trend[
            [
                "State",
                "2023 Accidents",
                "2024 Accidents",
                "Absolute change",
                "2023→2024 %",
                "2023 Killed",
                "2024 Killed",
            ]
        ]
        .sort_values(
            "2024 Accidents",
            ascending=False
        ),

        use_container_width=True,

        hide_index=True,
    )


# ============================================================
# TAB 5 — RISK INDICATORS
# ============================================================

with tabs[4]:

    st.subheader(
        f"Observed risk indicators — {selected_state}"
    )

    st.caption(
        "These are patterns observed in the supplied "
        "detailed 2018–2023 records. They are not proof "
        "of causation."
    )


    r1, r2, r3, r4 = st.columns(4)


    r1.metric(
        "Alcohol involvement",
        f'{selected_detail["Alcohol %"]:.1f}%'
    )


    r2.metric(
        "Night accidents",
        f'{selected_detail["Night %"]:.1f}%'
    )


    r3.metric(
        "Fatal-severity records",
        f'{selected_detail["Fatal detailed %"]:.1f}%'
    )


    r4.metric(
        "Top road type",
        str(
            selected_detail["Top road type"]
        )
    )


    sub = df[
        df["State Name"]
        .astype(str)
        .str.strip()
        == state_alias(selected_state)
    ].copy()


    if sub.empty:

        st.warning(
            "No detailed 2018–2023 records are available "
            "for this state in the supplied dataset."
        )

    else:

        left, right = st.columns(2)


        # Time
        time_counts = (

            sub["Time Window"]

            .value_counts()

            .reindex(
                [
                    "Morning",
                    "Afternoon",
                    "Evening",
                    "Night",
                    "Unknown"
                ],
                fill_value=0
            )

            .reset_index()
        )


        time_counts.columns = [
            "Time Window",
            "Accidents"
        ]


        fig = px.bar(

            time_counts,

            x="Time Window",

            y="Accidents",

            title=
                "Accidents by time window",
        )


        left.plotly_chart(
            fig,
            use_container_width=True
        )


        # Road type
        road_counts = (

            sub["Road Type"]

            .astype(str)

            .value_counts()

            .head(8)

            .reset_index()
        )


        road_counts.columns = [
            "Road Type",
            "Accidents"
        ]


        fig = px.bar(

            road_counts.sort_values(
                "Accidents"
            ),

            x="Accidents",

            y="Road Type",

            orientation="h",

            title=
                "Most represented road types",
        )


        right.plotly_chart(
            fig,
            use_container_width=True
        )


        w1, w2 = st.columns(2)


        # Weather
        weather_counts = (

            sub["Weather Conditions"]

            .astype(str)

            .value_counts()

            .head(8)

            .reset_index()
        )


        weather_counts.columns = [
            "Weather",
            "Accidents"
        ]


        fig = px.bar(

            weather_counts.sort_values(
                "Accidents"
            ),

            x="Accidents",

            y="Weather",

            orientation="h",

            title=
                "Most represented weather conditions",
        )


        w1.plotly_chart(
            fig,
            use_container_width=True
        )


        # Alcohol
        alcohol_counts = (

            sub["Alcohol Involvement"]

            .astype(str)

            .str.strip()

            .value_counts()

            .reset_index()
        )


        alcohol_counts.columns = [
            "Alcohol Involvement",
            "Accidents"
        ]


        fig = px.pie(

            alcohol_counts,

            names="Alcohol Involvement",

            values="Accidents",

            title=
                "Alcohol involvement in detailed records",
        )


        w2.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# TAB 6 — INTERVENTION PLAN
# ============================================================

with tabs[5]:

    st.subheader(
        f"Government intervention planning — "
        f"{selected_state}"
    )


    cards = intervention_action_cards(
        selected,
        selected_detail
    )


    # --------------------------------------------------------
    # Priority summary
    # --------------------------------------------------------

    st.markdown(
        "### Priority summary"
    )


    summary = (

        f"**{selected_state}** has a "
        f"**{selected['Priority']}** project-defined "
        f"government priority with a score of "
        f"**{selected['Government Priority Score']}/100**. "

        f"Official 2024 accident count is "
        f"**{int(selected['2024 Accidents']):,}**, "

        f"with **{int(selected['2024 Killed']):,} "
        f"fatalities**. "

        f"The official accident count changed by "
        f"**{selected['2023→2024 %']:.2f}%** "
        f"from 2023 to 2024."

    )


    st.write(summary)


    # --------------------------------------------------------
    # NEW INNOVATION
    # Risk → Evidence → Action
    # --------------------------------------------------------

    st.markdown(
        "### 🧠 Risk-to-Action Engine"
    )


    st.caption(
        "Each action connects an observed indicator "
        "to evidence and a government review action. "
        "These are recommendations for decision support, "
        "not automatic policy decisions."
    )


    for card in cards:

        if card["Priority"] == "HIGH":

            st.error(
                f"🚨 {card['Risk detected']}"
            )

        elif card["Priority"] == "MEDIUM":

            st.warning(
                f"⚠️ {card['Risk detected']}"
            )

        else:

            st.info(
                f"ℹ️ {card['Risk detected']}"
            )


        c1, c2 = st.columns(2)


        with c1:

            st.markdown(
                f"**Evidence**  \n"
                f"{card['Evidence']}"
            )


        with c2:

            st.markdown(
                f"**Recommended government action**  \n"
                f"{card['Government action']}"
            )


        st.caption(
            f"Verification required: "
            f"{card['Verification']}"
        )


        st.divider()


    # --------------------------------------------------------
    # Historical → 2024 evidence bridge
    # --------------------------------------------------------

    st.markdown(
        "### 🔄 Historical → 2024 evidence bridge"
    )


    st.caption(
        "Historical indicators come from the detailed "
        "2018–2023 accident-level dataset. The 2024 "
        "burden comes from the supplied official "
        "state-wise dataset."
    )


    evidence_table = pd.DataFrame(

        {
            "Evidence source": [

                "Official 2024 accident burden",

                "Official 2024 fatality burden",

                "Official 2023→2024 accident trend",

                "Detailed historical alcohol pattern (2018–2023)",

                "Detailed historical night-time pattern (2018–2023)",

                "Detailed historical dominant road type (2018–2023)",
            ],


            "Observed value": [

                f'{int(selected["2024 Accidents"]):,}',

                f'{int(selected["2024 Killed"]):,}',

                f'{selected["2023→2024 %"]:.2f}%',

                f'{selected_detail["Alcohol %"]:.1f}%',

                f'{selected_detail["Night %"]:.1f}%',

                str(
                    selected_detail["Top road type"]
                ),
            ],
        }
    )


    st.dataframe(

        evidence_table,

        use_container_width=True,

        hide_index=True,
    )


    st.warning(
        "Decision-support prototype only. Authorities "
        "would need local field verification, engineering "
        "assessment, policy review and current official "
        "data before acting."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(

    "Data basis: supplied accident-level dataset "
    "(2018–2023) and supplied official state-wise "
    "2020–2024 accident/fatality datasets. "

    "Intended end user: government road-safety "
    "authorities."

)


# ============================================================
# NEW FEATURE — RISK PRIORITY ENGINE
# ============================================================

st.markdown(
    "### 🧠 Risk Priority Engine — "
    "Why this state was prioritized"
)


st.caption(
    "The engine explains the project's score using "
    "transparent indicators. It does not predict "
    "accidents or establish causation."
)


driver_data = risk_priority_drivers(
    selected,
    selected_detail
)


driver_df = pd.DataFrame(
    driver_data,
    columns=[
        "Driver",
        "Interpretation"
    ]
)


st.dataframe(
    driver_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# NEW FEATURE — HISTORICAL → 2024 STATUS
# ============================================================

st.markdown(
    "### 🔄 Historical → 2024 status"
)


h1, h2 = st.columns(2)


h1.metric(
    "Historical detailed records",
    f'{int(selected_detail["Detailed records"]):,}',
)


h2.metric(
    "Official 2024 accidents",
    f'{int(selected["2024 Accidents"]):,}',
)


message = (
    f"**Historical evidence:** alcohol involvement "
    f"{selected_detail['Alcohol %']:.1f}%, "
    f"night-time records "
    f"{selected_detail['Night %']:.1f}%, "
    f"and dominant road type "
    f"'{selected_detail['Top road type']}'. "
    f"**Official 2024 status:** "
    f"{int(selected['2024 Accidents']):,} accidents "
    f"and {int(selected['2024 Killed']):,} fatalities."
)

st.info(message)

# ============================================================
# TAB 3 — INDIA PRIORITY MAP
# ============================================================

with tabs[2]:

    st.subheader(
        "India-wide government priority map"
    )

    coords = {

        "Andhra Pradesh": (15.9129, 79.7400),
        "Arunachal Pradesh": (28.2180, 94.7278),
        "Assam": (26.2006, 92.9376),
        "Bihar": (25.0961, 85.3131),
        "Chandigarh": (30.7333, 76.7794),
        "Chhattisgarh": (21.2787, 81.8661),
        "Delhi": (28.7041, 77.1025),
        "Goa": (15.2993, 74.1240),
        "Gujarat": (22.2587, 71.1924),
        "Haryana": (29.0588, 76.0856),
        "Himachal Pradesh": (31.1048, 77.1734),
        "J & K #": (33.7782, 76.5762),
        "Jharkhand": (23.6102, 85.2799),
        "Karnataka": (15.3173, 75.7139),
        "Kerala": (10.8505, 76.2711),
        "Madhya Pradesh": (22.9734, 78.6569),
        "Maharashtra": (19.7515, 75.7139),
        "Manipur": (24.6637, 93.9063),
        "Meghalaya": (25.4670, 91.3662),
        "Mizoram": (23.1645, 92.9376),
        "Nagaland": (26.1584, 94.5624),
        "Odisha": (20.9517, 85.0985),
        "Punjab": (31.1471, 75.3412),
        "Rajasthan": (27.0238, 74.2179),
        "Sikkim": (27.5330, 88.5122),
        "Tamil Nadu": (11.1271, 78.6569),
        "Telangana": (18.1124, 79.0193),
        "Tripura": (23.9408, 91.9882),
        "Uttar Pradesh": (26.8467, 80.9462),
        "Uttarakhand": (30.0668, 79.0193),
        "West Bengal": (22.9868, 87.8550),
        "Andaman & Nicobar Islands": (11.7401, 92.6586),
        "Dadra & Nagar Haveli and Daman & Diu": (20.1809, 73.0169),
        "Ladakh": (34.1526, 77.5771),
        "Lakshadweep": (10.5667, 72.6417),
        "Puducherry": (11.9416, 79.8083),
    }

    map_df = priority.copy()

    map_df["lat"] = map_df["State"].map(
        lambda x: coords.get(
            x,
            (np.nan, np.nan)
        )[0]
    )

    map_df["lon"] = map_df["State"].map(
        lambda x: coords.get(
            x,
            (np.nan, np.nan)
        )[1]
    )

    map_df = map_df.dropna(
        subset=["lat", "lon"]
    )

    fig = px.scatter_geo(

        map_df,

        lat="lat",
        lon="lon",

        size="Government Priority Score",

        color="Priority",

        hover_name="State",

        hover_data={
            "Government Priority Score": True,
            "2024 Accidents": ":,",
            "2024 Killed": ":,",
            "2023→2024 %": ":.2f",
            "lat": False,
            "lon": False,
        },

        projection="mercator",

        scope="asia",

        title=
            "Government intervention priority by state",

        size_max=30,

        category_orders={
            "Priority":
                ["HIGH", "MEDIUM", "LOW"]
        },
    )

    fig.update_geos(

        center={
            "lat": 22.5,
            "lon": 79
        },

        lataxis_range=[
            5,
            38
        ],

        lonaxis_range=[
            65,
            98
        ],

        showcountries=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="risk_time_chart"
    )

    st.info(
        "Map points represent approximate state/UT "
        "centroids. They are for state-level decision "
        "support and must not be interpreted as GPS-level "
        "accident hotspots."
    )


# ============================================================
# TAB 4 — 2023 → 2024 TREND
# ============================================================

with tabs[3]:

    st.subheader(
        "Official 2023 → 2024 change"
    )

    trend = priority.copy()

    trend["Absolute change"] = (
        trend["2024 Accidents"]
        - trend["2023 Accidents"]
    )

    left, right = st.columns(2)


    # Largest increases
    inc = (
        trend
        .sort_values(
            "Absolute change",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(

        inc.sort_values(
            "Absolute change"
        ),

        x="Absolute change",

        y="State",

        orientation="h",

        title=
            "Largest increases in accident count",

        text="Absolute change",
    )

    fig.update_traces(
        textposition="outside"
    )

    left.plotly_chart(
        fig,
        use_container_width=True,
        key="risk_time_chart_2"
    )


    # Largest decreases
    dec = (
        trend
        .sort_values(
            "Absolute change",
            ascending=True
        )
        .head(10)
    )

    fig = px.bar(

        dec.sort_values(
            "Absolute change"
        ),

        x="Absolute change",

        y="State",

        orientation="h",

        title=
            "Largest decreases in accident count",

        text="Absolute change",
    )

    fig.update_traces(
        textposition="outside"
    )

    right.plotly_chart(
        fig,
        use_container_width=True,
        key="risk_time_chart_3"
    )


    st.dataframe(

        trend[
            [
                "State",
                "2023 Accidents",
                "2024 Accidents",
                "Absolute change",
                "2023→2024 %",
                "2023 Killed",
                "2024 Killed",
            ]
        ]
        .sort_values(
            "2024 Accidents",
            ascending=False
        ),

        use_container_width=True,

        hide_index=True,
    )


# ============================================================
# TAB 5 — RISK INDICATORS
# ============================================================

with tabs[4]:

    st.subheader(
        f"Observed risk indicators — {selected_state}"
    )

    st.caption(
        "These are patterns observed in the supplied "
        "detailed 2018–2023 records. They are not proof "
        "of causation."
    )


    r1, r2, r3, r4 = st.columns(4)


    r1.metric(
        "Alcohol involvement",
        f'{selected_detail["Alcohol %"]:.1f}%'
    )


    r2.metric(
        "Night accidents",
        f'{selected_detail["Night %"]:.1f}%'
    )


    r3.metric(
        "Fatal-severity records",
        f'{selected_detail["Fatal detailed %"]:.1f}%'
    )


    r4.metric(
        "Top road type",
        str(
            selected_detail["Top road type"]
        )
    )


    sub = df[
        df["State Name"]
        .astype(str)
        .str.strip()
        == state_alias(selected_state)
    ].copy()


    if sub.empty:

        st.warning(
            "No detailed 2018–2023 records are available "
            "for this state in the supplied dataset."
        )

    else:

        left, right = st.columns(2)


        # Time
        time_counts = (

            sub["Time Window"]

            .value_counts()

            .reindex(
                [
                    "Morning",
                    "Afternoon",
                    "Evening",
                    "Night",
                    "Unknown"
                ],
                fill_value=0
            )

            .reset_index()
        )


        time_counts.columns = [
            "Time Window",
            "Accidents"
        ]


        fig = px.bar(

            time_counts,

            x="Time Window",

            y="Accidents",

            title=
                "Accidents by time window",
        )


        left.plotly_chart(
            fig,
            use_container_width=True,
            key="trend_increases_chart"
        )


        # Road type
        road_counts = (

            sub["Road Type"]

            .astype(str)

            .value_counts()

            .head(8)

            .reset_index()
        )


        road_counts.columns = [
            "Road Type",
            "Accidents"
        ]


        fig = px.bar(

            road_counts.sort_values(
                "Accidents"
            ),

            x="Accidents",

            y="Road Type",

            orientation="h",

            title=
                "Most represented road types",
        )


        right.plotly_chart(
            fig,
            use_container_width=True,
            key="trend_decrease_chart"
        )


        w1, w2 = st.columns(2)


        # Weather
        weather_counts = (

            sub["Weather Conditions"]

            .astype(str)

            .value_counts()

            .head(8)

            .reset_index()
        )


        weather_counts.columns = [
            "Weather",
            "Accidents"
        ]


        fig = px.bar(

            weather_counts.sort_values(
                "Accidents"
            ),

            x="Accidents",

            y="Weather",

            orientation="h",

            title=
                "Most represented weather conditions",
        )


        w1.plotly_chart(
            fig,
            use_container_width=True,
            key="risk_weather_chart"
        )


        # Alcohol
        alcohol_counts = (

            sub["Alcohol Involvement"]

            .astype(str)

            .str.strip()

            .value_counts()

            .reset_index()
        )


        alcohol_counts.columns = [
            "Alcohol Involvement",
            "Accidents"
        ]


        fig = px.pie(

            alcohol_counts,

            names="Alcohol Involvement",

            values="Accidents",

            title=
                "Alcohol involvement in detailed records",
        )


        w2.plotly_chart(
            fig,
            use_container_width=True,
            key="risk_alcohol_chart"
        )


# ============================================================
# TAB 6 — INTERVENTION PLAN
# ============================================================

with tabs[5]:

    st.subheader(
        f"Government intervention planning — "
        f"{selected_state}"
    )


    cards = intervention_action_cards(
        selected,
        selected_detail
    )


    # --------------------------------------------------------
    # Priority summary
    # --------------------------------------------------------

    st.markdown(
        "### Priority summary"
    )


    summary = (

        f"**{selected_state}** has a "
        f"**{selected['Priority']}** project-defined "
        f"government priority with a score of "
        f"**{selected['Government Priority Score']}/100**. "

        f"Official 2024 accident count is "
        f"**{int(selected['2024 Accidents']):,}**, "

        f"with **{int(selected['2024 Killed']):,} "
        f"fatalities**. "

        f"The official accident count changed by "
        f"**{selected['2023→2024 %']:.2f}%** "
        f"from 2023 to 2024."

    )


    st.write(summary)


    # --------------------------------------------------------
    # NEW INNOVATION
    # Risk → Evidence → Action
    # --------------------------------------------------------

    st.markdown(
        "### 🧠 Risk-to-Action Engine"
    )


    st.caption(
        "Each action connects an observed indicator "
        "to evidence and a government review action. "
        "These are recommendations for decision support, "
        "not automatic policy decisions."
    )


    for card in cards:

        if card["Priority"] == "HIGH":

            st.error(
                f"🚨 {card['Risk detected']}"
            )

        elif card["Priority"] == "MEDIUM":

            st.warning(
                f"⚠️ {card['Risk detected']}"
            )

        else:

            st.info(
                f"ℹ️ {card['Risk detected']}"
            )


        c1, c2 = st.columns(2)


        with c1:

            st.markdown(
                f"**Evidence**  \n"
                f"{card['Evidence']}"
            )


        with c2:

            st.markdown(
                f"**Recommended government action**  \n"
                f"{card['Government action']}"
            )


        st.caption(
            f"Verification required: "
            f"{card['Verification']}"
        )


        st.divider()


    # --------------------------------------------------------
    # Historical → 2024 evidence bridge
    # --------------------------------------------------------

    st.markdown(
        "### 🔄 Historical → 2024 evidence bridge"
    )


    st.caption(
        "Historical indicators come from the detailed "
        "2018–2023 accident-level dataset. The 2024 "
        "burden comes from the supplied official "
        "state-wise dataset."
    )


    evidence_table = pd.DataFrame(

        {
            "Evidence source": [

                "Official 2024 accident burden",

                "Official 2024 fatality burden",

                "Official 2023→2024 accident trend",

                "Detailed historical alcohol pattern (2018–2023)",

                "Detailed historical night-time pattern (2018–2023)",

                "Detailed historical dominant road type (2018–2023)",
            ],


            "Observed value": [

                f'{int(selected["2024 Accidents"]):,}',

                f'{int(selected["2024 Killed"]):,}',

                f'{selected["2023→2024 %"]:.2f}%',

                f'{selected_detail["Alcohol %"]:.1f}%',

                f'{selected_detail["Night %"]:.1f}%',

                str(
                    selected_detail["Top road type"]
                ),
            ],
        }
    )


    st.dataframe(

        evidence_table,

        use_container_width=True,

        hide_index=True,
    )


    st.warning(
        "Decision-support prototype only. Authorities "
        "would need local field verification, engineering "
        "assessment, policy review and current official "
        "data before acting."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(

    "Data basis: supplied accident-level dataset "
    "(2018–2023) and supplied official state-wise "
    "2020–2024 accident/fatality datasets. "

    "Intended end user: government road-safety "
    "authorities."

)