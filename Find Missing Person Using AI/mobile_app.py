import uuid
import json

import streamlit as st
import numpy as np

from pages.helper import db_queries
from pages.helper.data_models import PublicSubmissions
from pages.helper.utils import image_obj_to_numpy, extract_face_mesh_landmarks
from pages.helper.streamlit_helpers import require_login
from pages.helper.ui_components import load_css, confirm_card, empty_state

st.set_page_config("Report a Sighting", page_icon="📱", initial_sidebar_state="collapsed")
load_css()

# Branded header
st.markdown("""
<div style="text-align:center; margin-top:20px; margin-bottom:32px;">
    <div style="font-size:3rem; margin-bottom:8px;
                filter:drop-shadow(0 4px 16px rgba(79,139,249,0.35));">📱</div>
    <h2 style="margin:0; font-weight:800;
               background:linear-gradient(135deg, #FAFAFA 0%, #4F8BF9 100%);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
        Report a Sighting
    </h2>
    <p style="color:#7B8598; font-size:0.92rem; margin-top:8px; line-height:1.5;">
        Help reunite families — submit a photo and location of a person you've spotted
    </p>
    <div style="display:flex; justify-content:center; gap:20px; margin-top:14px;">
        <div style="background:rgba(46,204,113,0.1); border:1px solid rgba(46,204,113,0.2);
                    color:#2ECC71; padding:4px 14px; border-radius:16px; font-size:0.75rem; font-weight:600;">
            🔒 Secure & Anonymous
        </div>
        <div style="background:rgba(79,139,249,0.1); border:1px solid rgba(79,139,249,0.2);
                    color:#4F8BF9; padding:4px 14px; border-radius:16px; font-size:0.75rem; font-weight:600;">
            No Login Required
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

image_col, form_col = st.columns([1, 1.5], gap="large")
image_obj = None
save_flag = 0

with image_col:
    st.markdown('<div class="section-header">📷 Upload Photo</div>', unsafe_allow_html=True)
    image_obj = st.file_uploader(
        "Upload a clear face photo",
        type=["jpg", "jpeg", "png"],
        key="user_submission",
        label_visibility="collapsed",
    )
    if image_obj:
        unique_id = str(uuid.uuid4())

        with st.spinner("Processing image..."):
            uploaded_file_path = "./resources/" + str(unique_id) + ".jpg"
            with open(uploaded_file_path, "wb") as output_temporary_file:
                output_temporary_file.write(image_obj.read())

            st.image(image_obj, width='stretch')
            image_numpy = image_obj_to_numpy(image_obj)
            face_mesh = extract_face_mesh_landmarks(image_numpy)
            if face_mesh:
                st.markdown(confirm_card("✅", "Face Detected", "Ready for matching"), unsafe_allow_html=True)
            else:
                st.error("No face detected. Please use a clearer photo.")
    else:
        st.markdown(empty_state("📷", "No photo uploaded", "Upload a clear, front-facing photo for best results"), unsafe_allow_html=True)

if image_obj:
    with form_col:
        st.markdown('<div class="section-header">📋 Sighting Details</div>', unsafe_allow_html=True)
        with st.form(key="new_user_submission"):
            name = st.text_input("Your Name")

            phone_col, email_col = st.columns(2)
            mobile_number = phone_col.text_input("Your Mobile Number")
            email = email_col.text_input("Your Email")

            address = st.text_input("📍 Location where person was seen")
            birth_marks = st.text_input("Identifying features / Birth marks")

            st.write("")
            submit_bt = st.form_submit_button("📤 Submit Report", type="primary")

            public_submission_details = PublicSubmissions(
                submitted_by=name,
                location=address,
                email=email,
                face_mesh=json.dumps(face_mesh),
                id=unique_id,
                mobile=mobile_number,
                birth_marks=birth_marks,
                status="NF",
            )

            if submit_bt:
                db_queries.new_public_case(public_submission_details)
                # Log activity
                db_queries.log_activity(
                    case_id=unique_id,
                    case_type="public",
                    action="created",
                    description=f"Public sighting reported at {address or 'unknown location'} by {name or 'anonymous'}",
                    actor=name or "Public",
                )
                save_flag = 1

    if save_flag == 1:
        st.markdown(confirm_card("🎉", "Report Submitted Successfully", "Thank you for helping reunite a family. Your report will be matched against registered cases."), unsafe_allow_html=True)
        st.balloons()
