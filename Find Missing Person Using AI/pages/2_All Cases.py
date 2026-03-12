import streamlit as st
from pages.helper import db_queries
from pages.helper.streamlit_helpers import require_login
from pages.helper.ui_components import (
    load_css, page_header, status_badge, case_card_html, section_header,
    empty_state, similarity_score_card, timeline_event,
)

st.set_page_config(page_title="All Cases", page_icon="📂", layout="wide")
load_css()


def case_viewer(case):
    case = list(case)
    case_id = case.pop(0)
    matched_with_id = case.pop(-1)
    matched_with_details = None

    try:
        matched_with_id = matched_with_id.replace("{", "").replace("}", "")
    except:
        matched_with = None

    if matched_with_id:
        matched_with_details = db_queries.get_public_case_detail(matched_with_id)

    name, age, status, last_seen = case

    col_img, col_info, col_match = st.columns([1, 2, 2], gap="medium")

    with col_img:
        try:
            st.image("./resources/" + str(case_id) + ".jpg", width=180)
        except:
            st.markdown("""
            <div style="width:180px; height:180px; border-radius:14px;
                        background:rgba(26,31,46,0.8); border:2px dashed rgba(79,139,249,0.2);
                        display:flex; align-items:center; justify-content:center;
                        font-size:2.5rem; opacity:0.3;">🖼️</div>
            """, unsafe_allow_html=True)

    with col_info:
        badge = status_badge(status)
        st.markdown(f"""
        <div class="case-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <h4 style="margin:0; color:#FAFAFA;">{name}</h4>
                {badge}
            </div>
            <div class="info-row">
                <span class="info-label">Age</span>
                <span class="info-value">{age}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Last Seen</span>
                <span class="info-value">{last_seen or '—'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Case ID</span>
                <span class="info-value" style="font-size:0.75rem; font-family:monospace; color:#4F8BF9;">{case_id[:12]}...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_match:
        if matched_with_details:
            # Show similarity score if available
            match_score = db_queries.get_match_score_for_case(case_id)
            if match_score and match_score > 0:
                score_col, detail_col = st.columns([1, 1.5])
                with score_col:
                    st.markdown(similarity_score_card(match_score), unsafe_allow_html=True)
                with detail_col:
                    st.markdown(f"""
                    <div class="match-card" style="padding:16px;">
                        <div style="margin-bottom:10px;">
                            <span style="color:#2ECC71; font-weight:700; font-size:0.88rem;">🔗 Matched Sighting</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">📍 Location</span>
                            <span class="info-value">{matched_with_details[0][0]}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">👤 By</span>
                            <span class="info-value">{matched_with_details[0][1]}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">📱 Mobile</span>
                            <span class="info-value">{matched_with_details[0][2]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="match-card">
                    <div style="margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#2ECC71; font-weight:700; font-size:0.95rem;">🔗 Matched Sighting</span>
                        <span class="badge badge-matched">🟢 Match Found</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Location</span>
                        <span class="info-value">{matched_with_details[0][0]}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Reported By</span>
                        <span class="info-value">{matched_with_details[0][1]}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Mobile</span>
                        <span class="info-value">{matched_with_details[0][2]}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Birth Marks</span>
                        <span class="info-value">{matched_with_details[0][3] or '—'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="case-card" style="text-align:center; padding:32px 20px; opacity:0.7;">
                <div style="font-size:2rem; margin-bottom:8px; opacity:0.4;">🔍</div>
                <div style="color:#7B8598; font-size:0.88rem; font-weight:500;">No match yet</div>
                <div style="color:#5A6476; font-size:0.78rem; margin-top:4px;">Run matching to find potential sightings</div>
            </div>
            """, unsafe_allow_html=True)

    # Case Timeline expander
    activities = db_queries.get_case_activities(case_id)
    if activities:
        with st.expander(f"📜 Case Timeline ({len(activities)} events)"):
            st.markdown('<div class="case-card" style="padding:12px 16px;">', unsafe_allow_html=True)
            for act in activities:
                st.markdown(
                    timeline_event(act.action, act.description, act.timestamp, act.actor),
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)


def public_case_viewer(case: list) -> None:
    case = list(case)
    case_id = str(case.pop(0))

    status_val, location, mobile, birth_marks, submitted_on, submitted_by = case

    col_img, col_info = st.columns([1, 3], gap="medium")

    with col_img:
        try:
            st.image("./resources/" + case_id + ".jpg", width=180)
        except:
            st.markdown("""
            <div style="width:180px; height:180px; border-radius:14px;
                        background:rgba(26,31,46,0.8); border:2px dashed rgba(79,139,249,0.2);
                        display:flex; align-items:center; justify-content:center;
                        font-size:2.5rem; opacity:0.3;">🖼️</div>
            """, unsafe_allow_html=True)

    with col_info:
        badge = status_badge(status_val)
        st.markdown(f"""
        <div class="case-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <h4 style="margin:0; color:#FAFAFA;">Public Sighting Report</h4>
                {badge}
            </div>
            <div class="info-row">
                <span class="info-label">📍 Location</span>
                <span class="info-value">{location or '—'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">👤 Submitted By</span>
                <span class="info-value">{submitted_by or '—'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📱 Mobile</span>
                <span class="info-value">{mobile or '—'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">🔖 Birth Marks</span>
                <span class="info-value">{birth_marks or '—'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📅 Submitted On</span>
                <span class="info-value">{submitted_on}</span>
            </div>
            <div class="info-row">
                <span class="info-label">🆔 Case ID</span>
                <span class="info-value" style="font-size:0.75rem; font-family:monospace; color:#4F8BF9;">{case_id[:12]}...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


if "login_status" not in st.session_state:
    st.warning("⚠️ You don't have access to this page. Please log in first.")

elif st.session_state["login_status"]:
    user = st.session_state.user

    page_header("All Cases", "View and filter all registered cases and public submissions")
    st.write("")

    # Filters row
    filter_col1, filter_col2, _ = st.columns([1.2, 1, 2])
    status = filter_col1.selectbox(
        "Filter by Status",
        options=["All", "Not Found", "Found", "Public Cases"],
        format_func=lambda x: f"📋 {x}",
    )
    date = filter_col2.date_input("📅 Filter by Date")

    st.write("")

    if status == "Public Cases":
        cases_data = db_queries.fetch_public_cases(False, status)
        st.markdown(section_header("📱", "Public Submissions", len(cases_data) if cases_data else 0), unsafe_allow_html=True)
        if not cases_data:
            st.markdown(empty_state("📭", "No public submissions", "Public sightings submitted via the mobile app will appear here."), unsafe_allow_html=True)
        else:
            for case in cases_data:
                public_case_viewer(case)
                st.write("")
    else:
        cases_data = db_queries.fetch_registered_cases(user, status)
        st.markdown(section_header("📂", "Registered Cases", len(cases_data) if cases_data else 0), unsafe_allow_html=True)
        if not cases_data:
            st.markdown(empty_state("📭", "No cases found", "No cases match your current filter. Try a different status or register a new case."), unsafe_allow_html=True)
        else:
            for case in cases_data:
                case_viewer(case)
                st.write("")

else:
    st.warning("⚠️ You don't have access to this page. Please log in first.")
