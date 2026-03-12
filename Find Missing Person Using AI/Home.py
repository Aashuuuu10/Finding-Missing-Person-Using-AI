import yaml
import streamlit as st
from yaml import SafeLoader
import streamlit_authenticator as stauth
import plotly.graph_objects as go
import pandas as pd
from collections import Counter

from pages.helper import db_queries
from pages.helper.ui_components import load_css, stat_card, page_header, sidebar_profile, feature_card, section_header, timeline_event

st.set_page_config(
    page_title="Missing Persons Tracker AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

try:
    with open("login_config.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file 'login_config.yml' not found")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)


# ─── NOT LOGGED IN ───
if not st.session_state.get("authentication_status"):
    st.markdown("""
    <div style="text-align:center; margin-top:60px;">
        <div style="font-size:4rem; margin-bottom:12px; filter:drop-shadow(0 4px 16px rgba(79,139,249,0.35));">🔍</div>
        <h1 style="font-size:2.6rem; font-weight:800; margin:0;
                    background:linear-gradient(135deg, #FAFAFA 0%, #4F8BF9 100%);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
            Missing Persons Tracker
        </h1>
        <p style="color:#7B8598; font-size:1.05rem; margin-top:10px; margin-bottom:8px;">
            AI-powered face matching to help reunite families
        </p>
        <div style="display:flex; justify-content:center; gap:24px; margin-top:18px; margin-bottom:36px;">
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">🧠</div>
                <div style="color:#5A6476; font-size:0.75rem; margin-top:2px;">AI Matching</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">📊</div>
                <div style="color:#5A6476; font-size:0.75rem; margin-top:2px;">478 Landmarks</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">⚡</div>
                <div style="color:#5A6476; font-size:0.75rem; margin-top:2px;">Real-time</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 1.5, 1])
    with col_center:
        authenticator.login(location="main")

    if st.session_state.get("authentication_status") is False:
        st.error("Username or password is incorrect")
    elif st.session_state.get("authentication_status") is None:
        st.markdown("""
        <div style="text-align:center; margin-top:20px;">
            <p style="color:#5A6476; font-size:0.85rem;">
                🔒 Secure login &mdash; enter your credentials to access the admin panel
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ─── LOGGED IN — DASHBOARD ───
st.session_state["login_status"] = True
user_info = config["credentials"]["usernames"][st.session_state["username"]]
st.session_state["user"] = user_info["name"]

# Sidebar profile
sidebar_profile(
    name=user_info["name"],
    role=user_info["role"],
    area=user_info["area"],
    city=user_info["city"],
)
authenticator.logout("🚪 Logout", "sidebar")

# Page header
page_header("Dashboard", f"Welcome back, {user_info['name'].split()[0]}! Here's your overview.")

st.write("")

# ─── Stats ───
found_cases = db_queries.get_registered_cases_count(user_info["name"], "F")
not_found_cases = db_queries.get_registered_cases_count(user_info["name"], "NF")
total_cases = len(found_cases) + len(not_found_cases)
match_rate = round((len(found_cases) / total_cases * 100), 1) if total_cases > 0 else 0

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown(stat_card("📋", total_cases, "Total Cases"), unsafe_allow_html=True)
with col2:
    st.markdown(stat_card("✅", len(found_cases), "Found"), unsafe_allow_html=True)
with col3:
    st.markdown(stat_card("🔎", len(not_found_cases), "Not Found"), unsafe_allow_html=True)
with col4:
    st.markdown(stat_card("📊", f"{match_rate}%", "Match Rate"), unsafe_allow_html=True)

st.write("")
st.write("")

# ─── Charts & Quick Actions ───
chart_col, action_col = st.columns([1.2, 1], gap="large")

with chart_col:
    st.markdown("#### 📈 Case Status Overview")
    if total_cases > 0:
        fig = go.Figure(data=[go.Pie(
            labels=["Found", "Not Found"],
            values=[len(found_cases), len(not_found_cases)],
            hole=0.6,
            marker=dict(
                colors=["#2ECC71", "#E74C3C"],
                line=dict(color="#0E1117", width=3),
            ),
            textinfo="label+percent",
            textfont=dict(size=14, color="#FAFAFA"),
            hoverinfo="label+value",
            pull=[0.03, 0.03],
        )])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FAFAFA"),
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=320,
            annotations=[dict(
                text=f"<b style='font-size:22px'>{total_cases}</b><br><span style='color:#7B8598'>Total</span>",
                x=0.5, y=0.5, font_size=18,
                font_color="#FAFAFA",
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <h3>No data yet</h3>
            <p>Register your first case to see statistics here.</p>
        </div>
        """, unsafe_allow_html=True)

with action_col:
    st.markdown("#### ⚡ Quick Actions")
    st.write("")

    a1, a2 = st.columns(2, gap="small")
    with a1:
        st.markdown(feature_card("📝", "Register Case", "Add a new missing person"), unsafe_allow_html=True)
        st.page_link("pages/1_Register New Case.py", label="Go to Register →", icon="📝")
    with a2:
        st.markdown(feature_card("🔄", "Run Matching", "Find potential matches"), unsafe_allow_html=True)
        st.page_link("pages/3_Match Cases.py", label="Go to Match →", icon="🔄")

    st.write("")

    a3, a4 = st.columns(2, gap="small")
    with a3:
        st.markdown(feature_card("📂", "All Cases", "View all submitted cases"), unsafe_allow_html=True)
        st.page_link("pages/2_All Cases.py", label="Go to Cases →", icon="📂")
    with a4:
        st.markdown(feature_card("❓", "Help", "How to use this app"), unsafe_allow_html=True)
        st.page_link("pages/4_Help.py", label="Go to Help →", icon="❓")

# ─── Analytics Section ───
if total_cases > 0:
    st.write("")
    st.write("")
    st.markdown(section_header("📊", "Analytics"), unsafe_allow_html=True)
    st.write("")

    analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(["📅 Cases Over Time", "📍 Cases by Area", "👤 Age Distribution"])

    with analytics_tab1:
        cases_time_data = db_queries.get_cases_over_time(user_info["name"])
        if cases_time_data:
            df_time = pd.DataFrame(cases_time_data, columns=["submitted_on", "status"])
            df_time["date"] = pd.to_datetime(df_time["submitted_on"]).dt.date
            daily_counts = df_time.groupby("date").size().reset_index(name="count")
            daily_counts["date"] = pd.to_datetime(daily_counts["date"])
            # Cumulative
            daily_counts["cumulative"] = daily_counts["count"].cumsum()

            fig_time = go.Figure()
            fig_time.add_trace(go.Bar(
                x=daily_counts["date"], y=daily_counts["count"],
                name="New Cases",
                marker_color="#4F8BF9",
                opacity=0.7,
            ))
            fig_time.add_trace(go.Scatter(
                x=daily_counts["date"], y=daily_counts["cumulative"],
                name="Cumulative",
                line=dict(color="#2ECC71", width=3),
                yaxis="y2",
            ))
            fig_time.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA"),
                margin=dict(t=30, b=40, l=50, r=50),
                height=320,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Date"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="New Cases"),
                yaxis2=dict(title="Cumulative", overlaying="y", side="right", gridcolor="rgba(255,255,255,0.04)"),
                bargap=0.3,
            )
            st.plotly_chart(fig_time, width='stretch')
        else:
            st.info("No timeline data available yet.")

    with analytics_tab2:
        area_data = db_queries.get_cases_by_area(user_info["name"])
        if area_data:
            areas = [a[0] if a[0] else "Unknown" for a in area_data]
            area_counts = Counter(areas)
            sorted_areas = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            labels, values = zip(*sorted_areas) if sorted_areas else ([], [])

            fig_area = go.Figure(data=[go.Bar(
                x=list(values),
                y=list(labels),
                orientation="h",
                marker=dict(
                    color=list(values),
                    colorscale=[[0, "#1A1F2E"], [0.5, "#4F8BF9"], [1, "#7C4DFF"]],
                ),
                text=list(values),
                textposition="auto",
                textfont=dict(color="#FAFAFA"),
            )])
            fig_area.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA"),
                margin=dict(t=20, b=40, l=120, r=20),
                height=320,
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Case Count"),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_area, width='stretch')
        else:
            st.info("No area data available yet.")

    with analytics_tab3:
        age_data = db_queries.get_age_distribution(user_info["name"])
        if age_data:
            ages = []
            for a in age_data:
                try:
                    ages.append(int(float(a[0])))
                except (ValueError, TypeError):
                    pass
            if ages:
                fig_age = go.Figure(data=[go.Histogram(
                    x=ages,
                    nbinsx=15,
                    marker_color="#4F8BF9",
                    opacity=0.8,
                )])
                fig_age.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#FAFAFA"),
                    margin=dict(t=20, b=40, l=50, r=20),
                    height=320,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Age"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Count"),
                    bargap=0.1,
                )
                st.plotly_chart(fig_age, width='stretch')
            else:
                st.info("No valid age data to display.")
        else:
            st.info("No age data available yet.")

    # ─── Recent Activity Feed ───
    st.write("")
    st.markdown(section_header("🕐", "Recent Activity"), unsafe_allow_html=True)
    activities = db_queries.get_all_activities(limit=10)
    if activities:
        timeline_html = '<div class="case-card" style="padding:16px 20px;">'
        for act in activities:
            timeline_html += timeline_event(act.action, act.description, act.timestamp, act.actor)
        timeline_html += '</div>'
        st.markdown(timeline_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="case-card" style="text-align:center; padding:32px 20px; opacity:0.7;">
            <div style="font-size:2rem; margin-bottom:8px; opacity:0.4;">🕐</div>
            <div style="color:#7B8598; font-size:0.88rem;">No activity recorded yet</div>
            <div style="color:#5A6476; font-size:0.78rem; margin-top:4px;">Activities will appear here as cases are created and matched</div>
        </div>
        """, unsafe_allow_html=True)
