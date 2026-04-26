import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Global Hunger Index", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

* { font-family: 'Poppins', sans-serif; }

.stApp { background: #f7f8fc; }

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e4e7ec;
}

.card {
    background: #ffffff;
    border: 1px solid #e4e7ec;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}
.card .label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9aa5b4;
    margin-bottom: 6px;
}
.card .value {
    font-size: 28px;
    font-weight: 700;
    color: #1a1f36;
}
.card .sub {
    font-size: 11px;
    color: #9aa5b4;
    margin-top: 4px;
}

.header {
    background: #ffffff;
    border: 1px solid #e4e7ec;
    border-radius: 10px;
    padding: 28px 32px;
    margin-bottom: 20px;
}
.header h1 {
    font-size: 24px;
    font-weight: 700;
    color: #1a1f36;
    margin: 0 0 6px 0;
}
.header h1 span { color: #e85d26; }
.header p {
    font-size: 13px;
    color: #9aa5b4;
    margin: 0;
    line-height: 1.6;
}

.sec {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #1a1f36;
    margin: 24px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #e85d26;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)


SPECIAL_VALUES = ["—", "<5", "< 2.5", "*", ""]

REGION_MAP = {
    "Afghanistan":"South Asia","Bangladesh":"South Asia","Bhutan":"South Asia",
    "India":"South Asia","Nepal":"South Asia","Pakistan":"South Asia","Sri Lanka":"South Asia",
    "Cambodia":"Southeast Asia","Indonesia":"Southeast Asia","Lao PDR":"Southeast Asia",
    "Myanmar":"Southeast Asia","Philippines":"Southeast Asia","Timor-Leste":"Southeast Asia","Viet Nam":"Southeast Asia",
    "China":"East Asia","Korea (DPR)":"East Asia","Mongolia":"East Asia",
    "Armenia":"Central Asia","Azerbaijan":"Central Asia","Kazakhstan":"Central Asia",
    "Kyrgyzstan":"Central Asia","Tajikistan":"Central Asia","Uzbekistan":"Central Asia",
    "Algeria":"North Africa","Egypt":"North Africa","Morocco":"North Africa","Sudan":"North Africa","Tunisia":"North Africa",
    "Angola":"Sub-Saharan Africa","Benin":"Sub-Saharan Africa","Botswana":"Sub-Saharan Africa",
    "Burkina Faso":"Sub-Saharan Africa","Burundi":"Sub-Saharan Africa","Cabo Verde":"Sub-Saharan Africa",
    "Cameroon":"Sub-Saharan Africa","Central African Rep.":"Sub-Saharan Africa","Chad":"Sub-Saharan Africa",
    "Comoros":"Sub-Saharan Africa","Congo":"Sub-Saharan Africa","Congo, DR":"Sub-Saharan Africa",
    "Côte d'Ivoire":"Sub-Saharan Africa","Djibouti":"Sub-Saharan Africa","Equatorial Guinea":"Sub-Saharan Africa",
    "Eritrea":"Sub-Saharan Africa","Eswatini":"Sub-Saharan Africa","Ethiopia":"Sub-Saharan Africa",
    "Gabon":"Sub-Saharan Africa","Gambia":"Sub-Saharan Africa","Ghana":"Sub-Saharan Africa",
    "Guinea":"Sub-Saharan Africa","Guinea-Bissau":"Sub-Saharan Africa","Kenya":"Sub-Saharan Africa",
    "Lesotho":"Sub-Saharan Africa","Liberia":"Sub-Saharan Africa","Madagascar":"Sub-Saharan Africa",
    "Malawi":"Sub-Saharan Africa","Mali":"Sub-Saharan Africa","Mauritania":"Sub-Saharan Africa",
    "Mozambique":"Sub-Saharan Africa","Namibia":"Sub-Saharan Africa","Niger":"Sub-Saharan Africa",
    "Nigeria":"Sub-Saharan Africa","Rwanda":"Sub-Saharan Africa","Sao Tome & Principe":"Sub-Saharan Africa",
    "Senegal":"Sub-Saharan Africa","Sierra Leone":"Sub-Saharan Africa","Somalia":"Sub-Saharan Africa",
    "South Africa":"Sub-Saharan Africa","South Sudan":"Sub-Saharan Africa","Tanzania":"Sub-Saharan Africa",
    "Togo":"Sub-Saharan Africa","Uganda":"Sub-Saharan Africa","Zambia":"Sub-Saharan Africa","Zimbabwe":"Sub-Saharan Africa",
    "Iraq":"Middle East","Jordan":"Middle East","Lebanon":"Middle East","Syria":"Middle East",
    "Yemen":"Middle East","Bahrain":"Middle East","Qatar":"Middle East",
    "Bolivia (Plurinat. State of)":"Latin America","Brazil":"Latin America","Colombia":"Latin America",
    "Ecuador":"Latin America","El Salvador":"Latin America","Guatemala":"Latin America","Guyana":"Latin America",
    "Haiti":"Latin America","Honduras":"Latin America","Mexico":"Latin America","Nicaragua":"Latin America",
    "Panama":"Latin America","Paraguay":"Latin America","Peru":"Latin America","Venezuela":"Latin America",
    "Albania":"Europe","Belarus":"Europe","Bosnia & Herzegovina":"Europe","Bulgaria":"Europe",
    "Georgia":"Europe","Moldova":"Europe","North Macedonia":"Europe","Ukraine":"Europe","Serbia":"Europe",
}

GHI_YEARS = [2000, 2008, 2016, 2025]
GHI_COLS  = ["ghi_2000", "ghi_2008", "ghi_2016", "ghi_2025"]

METRIC_MAP = {
    "GHI Score":            {2000:"ghi_2000",      2008:"ghi_2008",      2016:"ghi_2016",      2025:"ghi_2025"},
    "Undernourishment (%)": {2000:"pou_2000_2002", 2008:"pou_2007_2009", 2016:"pou_2015_2017", 2025:"pou_2022_2024"},
    "Child Wasting (%)":    {2000:"wast_1998_2002",2008:"wast_2006_2010",2016:"wast_2014_2018",2025:"wast_2020_2024"},
    "Child Stunting (%)":   {2000:"stun_2000",     2008:"stun_2008",     2016:"stun_2016",     2025:"stun_2024"},
    "Child Mortality (%)":  {2000:"mort_2000",     2008:"mort_2008",     2016:"mort_2016",     2025:"mort_2023"},
}

CHART_BASE = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(family="Poppins", color="#1a1f36", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
)

COLORS = ["#e85d26", "#1a1f36", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"]


@st.cache_data
def load_data():
    df = pd.read_csv("globalhungerindex_2025.csv")
    df.columns = df.columns.str.strip().str.replace('"','',regex=False).str.replace('\ufeff','',regex=False)
    df.rename(columns={"cntry_name":"Country","cntry_iso3":"ISO3"}, inplace=True)
    for col in [c for c in df.columns if c not in ("Country","ISO3")]:
        df[col] = df[col].astype(str).str.strip().replace(SPECIAL_VALUES, np.nan)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Region"] = df["Country"].map(REGION_MAP).fillna("Other")
    return df


def severity(score):
    if pd.isna(score): return "No Data"
    if score < 10:     return "Low"
    if score < 20:     return "Moderate"
    if score < 30:     return "Serious"
    if score < 50:     return "Alarming"
    return "Extremely Alarming"


df = load_data()
df["Severity_2025"] = df["ghi_2025"].apply(severity)


with st.sidebar:
    st.markdown("**Global Hunger Index**")
    st.markdown("---")
    regions  = sorted(df["Region"].unique().tolist())
    sel_reg  = st.multiselect("Region", regions, default=regions)
    year     = st.select_slider("Year", GHI_YEARS, value=2025)
    metric   = st.selectbox("Metric", list(METRIC_MAP.keys()))
    top_n    = st.slider("Top N Countries", 5, 30, 15)
    st.markdown("---")
    st.caption("Source: Global Hunger Index 2025\n136 countries · 4 time periods")

metric_col  = METRIC_MAP[metric][year]
filtered_df = df[df["Region"].isin(sel_reg)].copy()
ghi_vals    = filtered_df[f"ghi_{year}"].dropna()
worst_idx   = ghi_vals.idxmax() if not ghi_vals.empty else None


st.markdown("""
<div class="header">
    <h1>Global <span>Hunger Index</span> Dashboard</h1>
    <p>Analysing hunger, undernourishment, child wasting, stunting and mortality across 136 countries from 2000 to 2025.</p>
</div>
""", unsafe_allow_html=True)


c1, c2, c3, c4 = st.columns(4)
cards = [
    ("Countries", len(filtered_df), "in selected regions"),
    (f"Avg GHI {year}", round(ghi_vals.mean(),1) if not ghi_vals.empty else "N/A", "global average"),
    (f"Highest GHI {year}", round(ghi_vals.max(),1) if not ghi_vals.empty else "N/A",
     filtered_df.loc[worst_idx,"Country"] if worst_idx else "N/A"),
    ("Alarming+", filtered_df[filtered_df["Severity_2025"].isin(["Alarming","Extremely Alarming"])].shape[0], "score 30 or above in 2025"),
]
for col, (label, value, sub) in zip([c1,c2,c3,c4], cards):
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)


HUNGER_SCALE = [
    [0.00, "#fff5f0"],
    [0.25, "#fdc89e"],
    [0.50, "#f99350"],
    [0.75, "#e85d26"],
    [1.00, "#9b3b16"],
]


st.markdown('<div class="sec">Geographic Distribution</div>', unsafe_allow_html=True)

map_df = filtered_df[["Country", "ISO3", metric_col]].dropna(subset=[metric_col])

if map_df.empty:
    st.info("No data available for the current selection.")
else:
    fig_map = px.choropleth(
        map_df,
        locations="ISO3",
        color=metric_col,
        hover_name="Country",
        color_continuous_scale=HUNGER_SCALE,
        labels={metric_col: metric},
    )
    fig_map.update_layout(
        **{**CHART_BASE, "margin": dict(l=10, r=10, t=50, b=10)},
        height=460,
        geo=dict(
            bgcolor="#ffffff",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#e4e7ec",
            landcolor="#f7f8fc",
            projection_type="natural earth",
        ),
        coloraxis_colorbar=dict(
            title=dict(text=metric, font=dict(size=11, color="#9aa5b4")),
            thickness=12,
            len=0.7,
            tickfont=dict(size=10, color="#1a1f36"),
            outlinewidth=0,
        ),
        title=dict(
            text=f"{metric} — {year}",
            font=dict(size=14, color="#1a1f36", weight=600),
            x=0.01, y=0.98, xanchor="left",
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)


st.markdown(f'<div class="sec">Top {top_n} Countries — {metric} ({year})</div>', unsafe_allow_html=True)

bar_df = (
    filtered_df[["Country", "Region", metric_col]]
    .dropna(subset=[metric_col])
    .sort_values(metric_col, ascending=False)
    .head(top_n)
    .iloc[::-1]
)

if bar_df.empty:
    st.info("No data available for the current selection.")
else:
    fig_bar = go.Figure(go.Bar(
        x=bar_df[metric_col],
        y=bar_df["Country"],
        orientation="h",
        marker=dict(color=COLORS[0], line=dict(width=0)),
        text=bar_df[metric_col].round(1),
        textposition="outside",
        textfont=dict(size=10, color="#1a1f36"),
        hovertemplate="<b>%{y}</b><br>" + metric + ": %{x:.1f}<extra></extra>",
    ))
    fig_bar.update_layout(
        **{**CHART_BASE, "margin": dict(l=10, r=40, t=20, b=30)},
        height=max(360, 22 * len(bar_df) + 80),
        xaxis=dict(
            title=dict(text=metric, font=dict(size=11, color="#9aa5b4")),
            gridcolor="#eef0f4", zerolinecolor="#e4e7ec",
            tickfont=dict(size=10, color="#1a1f36"),
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=11, color="#1a1f36"),
            automargin=True,
        ),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)