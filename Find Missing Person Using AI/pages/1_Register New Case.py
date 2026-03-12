import uuid
import numpy as np
import streamlit as st
import json
import base64

from pages.helper.data_models import RegisteredCases
from pages.helper import db_queries
from pages.helper.utils import image_obj_to_numpy, extract_face_mesh_landmarks
from pages.helper.streamlit_helpers import require_login
from pages.helper.ui_components import load_css, page_header, confirm_card, empty_state

st.set_page_config(page_title="Register New Case", page_icon="📝", layout="wide")
load_css()


def image_to_base64(image):
    return base64.b64encode(image).decode("utf-8")


def average_face_meshes(meshes: list) -> list:
    """Average multiple face mesh vectors for better accuracy."""
    if not meshes:
        return None
    if len(meshes) == 1:
        return meshes[0]
    arr = np.array(meshes, dtype=float)
    return arr.mean(axis=0).tolist()


if "login_status" not in st.session_state:
    st.warning("⚠️ You don't have access to this page. Please log in first.")

elif st.session_state["login_status"]:
    user = st.session_state.user

    page_header("Register New Case", "Fill in the details and upload photos of the missing person")

    # Step progress indicator
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:center; gap:8px; margin:16px 0 28px;">
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:30px; height:30px; border-radius:50%;
                        background:linear-gradient(135deg, #4F8BF9, #7C4DFF);
                        color:#FFF; display:flex; align-items:center; justify-content:center;
                        font-size:0.82rem; font-weight:700; box-shadow:0 2px 8px rgba(79,139,249,0.3);">1</div>
            <span style="color:#FAFAFA; font-weight:600; font-size:0.88rem;">Upload Photos</span>
        </div>
        <div style="width:48px; height:2px; background:rgba(79,139,249,0.25); border-radius:2px;"></div>
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:30px; height:30px; border-radius:50%;
                        background:rgba(79,139,249,0.15); border:1px solid rgba(79,139,249,0.3);
                        color:#7B8598; display:flex; align-items:center; justify-content:center;
                        font-size:0.82rem; font-weight:700;">2</div>
            <span style="color:#7B8598; font-weight:500; font-size:0.88rem;">Fill Details</span>
        </div>
        <div style="width:48px; height:2px; background:rgba(79,139,249,0.15); border-radius:2px;"></div>
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:30px; height:30px; border-radius:50%;
                        background:rgba(79,139,249,0.15); border:1px solid rgba(79,139,249,0.3);
                        color:#7B8598; display:flex; align-items:center; justify-content:center;
                        font-size:0.82rem; font-weight:700;">3</div>
            <span style="color:#7B8598; font-weight:500; font-size:0.88rem;">Submit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    image_col, form_col = st.columns([1, 1.5], gap="large")
    image_objects = None
    save_flag = 0
    face_meshes_collected = []
    unique_id = None

    with image_col:
        st.markdown('<div class="section-header">📷 Upload Photos</div>', unsafe_allow_html=True)
        st.caption("Upload multiple photos for better matching accuracy")
        image_objects = st.file_uploader(
            "Upload clear face photos (JPG/PNG)",
            type=["jpg", "jpeg", "png"],
            key="new_case",
            label_visibility="collapsed",
            accept_multiple_files=True,
        )

        if image_objects:
            unique_id = str(uuid.uuid4())
            photo_count = len(image_objects)

            # Save first photo as the primary case image
            primary_file_path = "./resources/" + str(unique_id) + ".jpg"
            first_img = image_objects[0]
            first_img.seek(0)
            with open(primary_file_path, "wb") as f:
                f.write(first_img.read())

            # Process all photos
            with st.spinner(f"Processing {photo_count} photo(s)..."):
                # Show thumbnails in a grid
                thumb_cols = st.columns(min(photo_count, 3))
                for idx, img_obj in enumerate(image_objects):
                    img_obj.seek(0)
                    with thumb_cols[idx % 3]:
                        st.image(img_obj, width='stretch', caption=f"Photo {idx + 1}")

                    # Save additional photos
                    if idx > 0:
                        extra_path = f"./resources/{unique_id}_{idx}.jpg"
                        img_obj.seek(0)
                        with open(extra_path, "wb") as f:
                            f.write(img_obj.read())

                    # Extract face mesh
                    img_obj.seek(0)
                    image_numpy = image_obj_to_numpy(img_obj)
                    mesh = extract_face_mesh_landmarks(image_numpy)
                    if mesh:
                        face_meshes_collected.append(mesh)

                if face_meshes_collected:
                    st.markdown(confirm_card(
                        "✅",
                        f"Faces Detected in {len(face_meshes_collected)}/{photo_count} photo(s)",
                        f"{'Averaged ' if len(face_meshes_collected) > 1 else ''}478 landmarks extracted — more photos = better accuracy"
                    ), unsafe_allow_html=True)
                else:
                    st.error("No faces detected in any photo. Please upload clearer photos with visible faces.")
        else:
            st.markdown(empty_state("📷", "No photos uploaded", "Upload one or more clear, front-facing photos for best results"), unsafe_allow_html=True)

    if image_objects and face_meshes_collected:
        # Average face meshes from all photos
        final_face_mesh = average_face_meshes(face_meshes_collected)
        photo_count = len(image_objects)

        with form_col:
            st.markdown('<div class="section-header">📋 Case Information</div>', unsafe_allow_html=True)
            with st.form(key="new_case"):
                st.markdown("**Missing Person Details**")
                name_col, father_col = st.columns(2)
                name = name_col.text_input("Full Name")
                fathers_name = father_col.text_input("Father's Name")

                age_col, mobile_col, adhaar_col = st.columns(3)
                age = age_col.number_input("Age", min_value=3, max_value=100, value=10, step=1)
                mobile_number = mobile_col.text_input("Mobile Number")
                adhaar_card = adhaar_col.text_input("Aadhaar Card")

                address = st.text_input("Address")

                seen_col, mark_col = st.columns(2)
                last_seen = seen_col.text_input("Last Seen Location")
                birthmarks = mark_col.text_input("Birth Marks / Identifying Features")

                description = st.text_area("Description (optional)", height=80)

                st.write("")
                st.markdown("**Complainant Details**")
                comp_name_col, comp_phone_col = st.columns(2)
                complainant_name = comp_name_col.text_input("Complainant Name")
                complainant_phone = comp_phone_col.text_input("Complainant Phone")

                st.write("")
                submit_bt = st.form_submit_button("📝 Register Case", type="primary")

                new_case_details = RegisteredCases(
                    id=unique_id,
                    submitted_by=user,
                    name=name,
                    fathers_name=fathers_name,
                    age=age,
                    complainant_mobile=mobile_number,
                    complainant_name=complainant_name,
                    face_mesh=json.dumps(final_face_mesh),
                    adhaar_card=adhaar_card,
                    birth_marks=birthmarks,
                    address=address,
                    last_seen=last_seen,
                    status="NF",
                    matched_with="",
                    photo_count=photo_count,
                )

                if submit_bt:
                    db_queries.register_new_case(new_case_details)
                    # Log activity
                    db_queries.log_activity(
                        case_id=unique_id,
                        case_type="registered",
                        action="created",
                        description=f"Case registered for {name or 'Unknown'} with {photo_count} photo(s)",
                        actor=user,
                    )
                    if photo_count > 1:
                        db_queries.log_activity(
                            case_id=unique_id,
                            case_type="registered",
                            action="photo_added",
                            description=f"{photo_count} photos uploaded, face meshes averaged for better accuracy",
                            actor=user,
                        )
                    save_flag = 1

        if save_flag:
            st.markdown(confirm_card("🎉", "Case Registered Successfully", f"Case ID: {unique_id[:12]}... — {photo_count} photo(s) processed. The case is now active and ready for matching."), unsafe_allow_html=True)
            st.balloons()

else:
    st.warning("⚠️ You don't have access to this page. Please log in first.")
