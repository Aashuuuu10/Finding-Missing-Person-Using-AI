import streamlit as st

from pages.helper import db_queries, match_algo, train_model
from pages.helper.streamlit_helpers import require_login
from pages.helper.ui_components import (
    load_css, page_header, status_badge, empty_state, confirm_card,
    section_header, similarity_score_card,
)

st.set_page_config(page_title="Match Cases", page_icon="🔄", layout="wide")
load_css()


def case_viewer(registered_case_id, public_case_id, score=None, user=""):
    try:
        case_details = db_queries.get_registered_case_detail(registered_case_id)[0]
        name, mobile, age, last_seen, birth_marks = case_details

        col_img, col_info, col_action = st.columns([1, 2, 1.2], gap="medium")

        with col_img:
            try:
                st.image(
                    "./resources/" + registered_case_id + ".jpg",
                    width=200,
                )
            except Exception:
                st.markdown("""
                <div style="width:200px; height:200px; border-radius:14px;
                            background:rgba(26,31,46,0.8); border:2px dashed rgba(79,139,249,0.2);
                            display:flex; align-items:center; justify-content:center;
                            font-size:2.5rem; opacity:0.3;">🖼️</div>
                """, unsafe_allow_html=True)

        with col_info:
            st.markdown(f"""
            <div class="match-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <h4 style="margin:0; color:#FAFAFA;">{name}</h4>
                    <span class="badge badge-matched">🟢 Match Found</span>
                </div>
                <div class="info-row">
                    <span class="info-label">👤 Age</span>
                    <span class="info-value">{age}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📱 Contact</span>
                    <span class="info-value">{mobile or '—'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📍 Last Seen</span>
                    <span class="info-value">{last_seen or '—'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🔖 Birth Marks</span>
                    <span class="info-value">{birth_marks or '—'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_action:
            if score is not None:
                st.markdown(similarity_score_card(score), unsafe_allow_html=True)
            else:
                st.markdown(confirm_card("✅", "Match Confirmed", "Status updated automatically"), unsafe_allow_html=True)

        # Update status with score
        if score is not None:
            db_queries.update_found_status_with_score(registered_case_id, public_case_id, score)
        else:
            db_queries.update_found_status(registered_case_id, public_case_id)

        # Log activity
        db_queries.log_activity(
            case_id=registered_case_id,
            case_type="registered",
            action="matched",
            description=f"{name} matched with public sighting (score: {score or 'N/A'}%)",
            actor=user,
        )
        db_queries.log_activity(
            case_id=public_case_id,
            case_type="public",
            action="matched",
            description=f"Matched with registered case for {name}",
            actor=user,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        st.error(f"Error loading case: {str(e)}")


if "login_status" not in st.session_state:
    st.warning("⚠️ You don't have access to this page. Please log in first.")

elif st.session_state["login_status"]:
    user = st.session_state.user

    page_header("Match Cases", "Run AI-powered face matching to find potential matches")
    st.write("")

    # Action buttons
    col1, col2, _ = st.columns([1.2, 1, 3])
    refresh_bt = col1.button("🔄 Run Matching", type="primary")
    st.write("")

    if refresh_bt:
        with st.status("🧠 AI Processing...", expanded=True) as status_bar:
            st.write("📊 **Step 1/3:** Loading registered cases...")
            result = train_model.train(user)

            st.write("🧠 **Step 2/3:** Training KNN model on face data...")
            import time
            time.sleep(0.5)  # Brief pause for visual feedback

            st.write("🔍 **Step 3/3:** Scanning public submissions for matches...")
            matched_ids = match_algo.match()
            scores = matched_ids.get("scores", {})

            if matched_ids["status"]:
                if not matched_ids["result"]:
                    status_bar.update(label="✅ Complete — No matches found", state="complete")
                    st.write("")
                    st.markdown(empty_state("🔍", "No Matches Found", "No public submissions matched any registered cases. New sightings may arrive later."), unsafe_allow_html=True)
                else:
                    match_count = sum(len(v) for v in matched_ids["result"].values())
                    status_bar.update(
                        label=f"✅ Complete — {match_count} match(es) found!",
                        state="complete",
                    )
                    st.write("")
                    st.markdown(section_header("🎯", "Match Results", match_count), unsafe_allow_html=True)
                    st.write("")

                    for matched_id, submitted_case_ids in matched_ids["result"].items():
                        score = scores.get(matched_id)
                        case_viewer(matched_id, submitted_case_ids[0], score=score, user=user)
                        st.divider()
            else:
                status_bar.update(label="⚠️ Could not complete matching", state="error")
                st.warning(f"⚠️ {matched_ids.get('message', 'Unknown error')}")
    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div style="font-size:5rem; margin-bottom:16px; opacity:0.25;
                        filter:drop-shadow(0 4px 16px rgba(79,139,249,0.2));">🧠</div>
            <h3 style="color:#8B95A5; font-weight:600;">Ready to scan for matches</h3>
            <p style="color:#5A6476; font-size:0.92rem; max-width:450px; margin:10px auto 0; line-height:1.6;">
                Click <b style="color:#4F8BF9;">Run Matching</b> to train the AI model and scan all public
                submissions against your registered missing persons.
            </p>
            <div style="display:flex; justify-content:center; gap:32px; margin-top:28px;">
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;">📊</div>
                    <div style="color:#5A6476; font-size:0.78rem; margin-top:4px;">Train Model</div>
                </div>
                <div style="color:rgba(79,139,249,0.3); font-size:1.2rem; line-height:2.5;">→</div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;">🔍</div>
                    <div style="color:#5A6476; font-size:0.78rem; margin-top:4px;">Scan Faces</div>
                </div>
                <div style="color:rgba(79,139,249,0.3); font-size:1.2rem; line-height:2.5;">→</div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;">🎯</div>
                    <div style="color:#5A6476; font-size:0.78rem; margin-top:4px;">Find Matches</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("⚠️ You don't have access to this page. Please log in first.")
