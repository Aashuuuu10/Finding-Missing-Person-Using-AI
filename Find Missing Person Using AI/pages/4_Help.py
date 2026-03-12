import streamlit as st
from pages.helper.ui_components import load_css, page_header, step_card

st.set_page_config(page_title="Help", page_icon="❓", layout="wide")
load_css()

page_header("Help & Documentation", "Learn how to use the Missing Persons Tracker effectively")

st.write("")

# How it works — glass card
st.markdown("""
<div class="glass-card" style="margin-bottom:28px;">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
        <div style="width:44px; height:44px; border-radius:12px;
                    background:linear-gradient(135deg, #4F8BF9, #7C4DFF);
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.3rem; box-shadow:0 4px 12px rgba(79,139,249,0.3);">🧠</div>
        <h4 style="margin:0; color:#FAFAFA; font-size:1.2rem;">How It Works</h4>
    </div>
    <p style="color:#B0B8C8; line-height:1.8; margin:0; font-size:0.95rem;">
        This application uses <b style="color:#4F8BF9;">AI-powered face mesh detection</b> (MediaPipe) to extract
        <b style="color:#FAFAFA;">478 facial landmarks</b> from uploaded photos. When a match is requested, it
        compares the facial geometry of registered missing persons against public sightings using a
        <b style="color:#4F8BF9;">K-Nearest Neighbors (KNN)</b> algorithm to find potential matches with
        high accuracy.
    </p>
</div>
""", unsafe_allow_html=True)

# Steps
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(step_card(1, "📝", "Register a Case",
        "Go to <b>Register New Case</b> and upload a clear photo of the missing person. "
        "Fill in all available details — name, age, last seen location, identifying marks, etc."
    ), unsafe_allow_html=True)

with col2:
    st.markdown(step_card(2, "📱", "Collect Public Reports",
        "Anyone can submit a sighting via the <b>Public Submission</b> portal (mobile app). "
        "Upload a photo and provide location details where the person was seen."
    ), unsafe_allow_html=True)

with col3:
    st.markdown(step_card(3, "🔄", "Run AI Matching",
        "Go to <b>Match Cases</b> and click <b>Run Matching</b>. The AI will compare all "
        "public submissions against registered cases and highlight potential matches."
    ), unsafe_allow_html=True)

st.write("")
st.write("")

# Technology stack info
st.markdown("""
<div class="glass-card" style="margin-bottom:28px;">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
        <div style="width:44px; height:44px; border-radius:12px;
                    background:linear-gradient(135deg, #2ECC71, #27AE60);
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.3rem; box-shadow:0 4px 12px rgba(46,204,113,0.3);">⚙️</div>
        <h4 style="margin:0; color:#FAFAFA; font-size:1.2rem;">Technology Stack</h4>
    </div>
    <div style="display:flex; flex-wrap:wrap; gap:10px;">
        <span style="background:rgba(79,139,249,0.1); border:1px solid rgba(79,139,249,0.2);
                     color:#4F8BF9; padding:6px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">
            MediaPipe Face Mesh
        </span>
        <span style="background:rgba(46,204,113,0.1); border:1px solid rgba(46,204,113,0.2);
                     color:#2ECC71; padding:6px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">
            KNN Algorithm
        </span>
        <span style="background:rgba(241,196,15,0.1); border:1px solid rgba(241,196,15,0.2);
                     color:#F1C40F; padding:6px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">
            478 Face Landmarks
        </span>
        <span style="background:rgba(155,89,182,0.1); border:1px solid rgba(155,89,182,0.2);
                     color:#9B59B6; padding:6px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">
            Streamlit
        </span>
        <span style="background:rgba(231,76,60,0.1); border:1px solid rgba(231,76,60,0.2);
                     color:#E74C3C; padding:6px 16px; border-radius:20px; font-size:0.82rem; font-weight:600;">
            SQLite Database
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# FAQ
st.markdown('<div class="section-header">❓ Frequently Asked Questions</div>', unsafe_allow_html=True)
st.write("")

with st.expander("What photo formats are supported?"):
    st.markdown("""
    **JPG, JPEG, and PNG** formats are supported.

    For best results:
    - Use a **clear, well-lit** front-facing photo
    - Ensure the **full face is visible** (no sunglasses or masks)
    - Minimum recommended resolution: **480 x 480px**
    """)

with st.expander("How accurate is the face matching?"):
    st.markdown("""
    The system extracts **478 facial landmarks** (1,434 data points) for each face.

    Accuracy depends on:
    - **Photo quality** — higher resolution gives better results
    - **Lighting** — even lighting reduces false negatives
    - **Face angle** — front-facing photos work best
    - **Distance threshold** — configurable sensitivity (default: 3.0)

    Lower KNN distances indicate closer matches.
    """)

with st.expander("Can anyone submit a public sighting?"):
    st.markdown("""
    **Yes!** The public submission portal does not require login.

    Anyone who spots a person matching a missing person's description can submit a report
    through the mobile-friendly **Report a Sighting** page. All submissions are stored securely
    and compared during matching.
    """)

with st.expander("What happens when a match is found?"):
    st.markdown("""
    When a match is detected:
    1. The registered case status is automatically updated to **"Found"**
    2. The matched public submission is **linked** to the case
    3. Contact details from the sighting are made available to the case officer
    4. Both records are updated in the database
    """)

with st.expander("How do I change my password?"):
    st.markdown("Contact the **system administrator** to update your credentials in the configuration file (`login_config.yml`).")

st.write("")
st.write("")

# Contact card
st.markdown("""
<div class="glass-card" style="text-align:center;">
    <div style="font-size:2.2rem; margin-bottom:10px; filter:drop-shadow(0 2px 8px rgba(79,139,249,0.3));">💬</div>
    <h4 style="color:#FAFAFA; margin:0 0 8px;">Need More Help?</h4>
    <p style="color:#7B8598; margin:0; font-size:0.92rem; line-height:1.6;">
        Contact the system administrator or raise an issue for technical support.<br>
        <span style="color:#4F8BF9; font-weight:600;">We're here to help reunite families.</span>
    </p>
</div>
""", unsafe_allow_html=True)