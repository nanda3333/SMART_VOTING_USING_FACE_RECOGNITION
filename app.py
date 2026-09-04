import streamlit as st
import pandas as pd
from core.db import (
    init_db, register_voter, cast_vote,
    load_all_embeddings, get_analytics,
    get_all_voters, delete_voter_by_hash, delete_voter_by_id
)
from core.face_engine import generate_embedding, verify_voter_face

st.set_page_config(
    page_title="Biometric Polling Portal",
    page_icon="🗳️",
    layout="wide"
)

init_db()

if "authenticated_voter" not in st.session_state:
    st.session_state.authenticated_voter = None
if "auth_confidence" not in st.session_state:
    st.session_state.auth_confidence = 0.0

st.sidebar.title("Voting Portal")
page = st.sidebar.radio(
    "Select Interface",
    ["Overview", "Voter Enrollment", "Voting Booth", "Admin Telemetrics"]
)

# -------------------------------------------------------------
# 1. OVERVIEW
# -------------------------------------------------------------
if page == "Overview":
    st.title("Smart Voting System")
    st.markdown("""
    Automated biometric polling architecture using **FaceNet512** deep embeddings,
    salted SHA-512 cryptographic masking, and transactional SQLite audit tables.
    """)

    vote_counts, total_reg, total_cast = get_analytics()

    col1, col2, col3 = st.columns(3)
    col1.metric("Enrolled Citizens", total_reg)
    col2.metric("Total Ballots Cast", total_cast)
    turnout = (total_cast / total_reg * 100) if total_reg > 0 else 0.0
    col3.metric("Voter Turnout", f"{turnout:.1f}%")

    st.markdown("---")
    st.subheader("System Pipeline")
    st.code("""
[Webcam Stream] ──> [Face Alignment & Normalization]
                 ──> [512D Biometric Embeddings (FaceNet512)]
                 ──> [Cosine Distance Verification (Threshold <= 0.40)]
                 ──> [Salted SHA-512 Match & Atomic SQL Ledger]
    """, language="text")

# -------------------------------------------------------------
# 2. VOTER ENROLLMENT
# -------------------------------------------------------------
elif page == "Voter Enrollment":
    st.title("Voter Identity Enrollment")
    st.write("Register a new voter identity and record their biometric signature.")

    with st.form("enrollment_form"):
        col_id, col_name = st.columns(2)
        with col_id:
            voter_id = st.text_input("Unique Identification Number", placeholder="e.g. DOC-1234567")
        with col_name:
            full_name = st.text_input("Full Name", placeholder="e.g. John Doe")

        mobile_num = st.text_input("Mobile Number", placeholder="e.g. +91 9876543210")

        st.info("Ensure adequate lighting and look directly into the camera.")
        cam_shot = st.camera_input("Biometric Photo Capture")
        submit_btn = st.form_submit_button("Complete Registration", type="primary")

    if submit_btn:
        if not voter_id.strip():
            st.error("Unique Identification field cannot be empty.")
        elif not full_name.strip():
            st.error("Full Name field cannot be empty.")
        elif not mobile_num.strip():
            st.error("Mobile Number field cannot be empty.")
        elif not cam_shot:
            st.error("Please capture a photo before submitting.")
        else:
            with st.spinner("Extracting 512D deep facial embedding..."):
                embedding = generate_embedding(cam_shot.getvalue())

            if embedding is None:
                st.error("No valid face detected. Please ensure your face is uncovered, centered, and well-lit.")
            else:
                success = register_voter(voter_id, full_name, mobile_num, embedding)
                if success:
                    st.success(f"Voter {full_name.strip()} successfully registered with biometric verification.")
                else:
                    st.warning("This unique identification number is already registered.")

# -------------------------------------------------------------
# 3. VOTING BOOTH
# -------------------------------------------------------------
elif page == "Voting Booth":
    st.title("Electronic Balloting Booth")

    if not st.session_state.authenticated_voter:
        st.subheader("Step 1: Face Verification")
        st.write("Look into the camera to authenticate against the registered database.")

        booth_shot = st.camera_input("Voter Authentication Sensor")

        if booth_shot:
            with st.spinner("Verifying biometric profile..."):
                probe_embedding = generate_embedding(booth_shot.getvalue())

                if probe_embedding is None:
                    st.error("Face not detected. Please look directly into the camera.")
                else:
                    registry = load_all_embeddings()
                    matched_hash, distance = verify_voter_face(probe_embedding, registry)

                    if matched_hash:
                        st.session_state.authenticated_voter = matched_hash
                        st.session_state.auth_confidence = (1.0 - distance) * 100
                        st.rerun()
                    else:
                        st.error(f"Authentication Failed: No matching registered record found (Cosine Distance: {distance:.2f}).")

    else:
        st.success(f"Identity Verified! Match Confidence: {st.session_state.auth_confidence:.1f}%")
        st.subheader("Step 2: Cast Your Ballot")

        candidates = ["Party Alpha (PA)", "Party Beta (PB)", "Party Gamma (PG)", "NOTA (None of the Above)"]
        chosen_party = st.radio("Select Choice:", candidates)

        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("Submit Vote", type="primary"):
                ok, msg = cast_vote(st.session_state.authenticated_voter, chosen_party)
                if ok:
                    st.success(msg)
                    st.balloons()
                    st.session_state.authenticated_voter = None
                    st.session_state.auth_confidence = 0.0
                else:
                    st.error(msg)
                    st.session_state.authenticated_voter = None
                    st.session_state.auth_confidence = 0.0

        with c2:
            if st.button("Cancel Authentication"):
                st.session_state.authenticated_voter = None
                st.session_state.auth_confidence = 0.0
                st.rerun()

# -------------------------------------------------------------
# 4. ADMIN TELEMETRICS & REGISTRY MANAGEMENT
# -------------------------------------------------------------
elif page == "Admin Telemetrics":
    st.title("Administrative Telemetrics & Registry Operations")

    admin_pass = st.sidebar.text_input("Admin Passcode", type="password")
    if admin_pass == "admin@2026":
        tab_analytics, tab_manage = st.tabs(["📊 Election Tallies", "⚙️ Voter Registry Management"])

        # TAB 1: Election Analytics & Vote Export
        with tab_analytics:
            vote_counts, total_reg, total_cast = get_analytics()

            m1, m2, m3 = st.columns(3)
            m1.metric("Registered Voters", total_reg)
            m2.metric("Ballots Cast", total_cast)
            turnout = (total_cast / total_reg * 100) if total_reg > 0 else 0.0
            m3.metric("Turnout", f"{turnout:.1f}%")

            if vote_counts:
                df_votes = pd.DataFrame(vote_counts, columns=["Party", "Total Votes"])
                st.subheader("Live Ballot Count")
                st.bar_chart(df_votes.set_index("Party"))
                st.dataframe(df_votes, use_container_width=True)

                csv_export = df_votes.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Export Election Tallies (CSV)",
                    data=csv_export,
                    file_name="Election_Tally_Summary.csv",
                    mime="text/csv"
                )
            else:
                st.info("No ballots recorded in the ledger yet.")

        # TAB 2: Voter Registry Directory & Deletion
        with tab_manage:
            st.subheader("Voter Directory & Administrative Purge")
            st.caption("Inspect enrolled voter details, export official directory records, or delete inactive voters.")

            voters_records = get_all_voters()

            if voters_records:
                df_all = pd.DataFrame(voters_records)

                # Export voter details (Unique ID, Name, Mobile Number)
                df_export = df_all[["Unique Voter ID", "Full Name", "Mobile Number", "Voted Status", "Registered At"]]

                st.markdown("##### 📥 Export Voter Directory")
                voter_csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Voter Directory (CSV)",
                    data=voter_csv,
                    file_name="Enrolled_Voters_Directory.csv",
                    mime="text/csv",
                    type="primary"
                )

                st.markdown("---")
                st.markdown("##### Registered Voters List")
                st.dataframe(df_export, use_container_width=True)

                st.markdown("---")
                st.markdown("##### De-register / Delete Voter Records")
                col_del1, col_del2 = st.columns(2)

                with col_del1:
                    st.markdown("###### Option A: Delete by Unique ID")
                    del_id = st.text_input("Enter Voter ID to Delete", placeholder="e.g. DOC-1234567")
                    if st.button("Delete Voter Record", type="secondary"):
                        if del_id.strip():
                            if delete_voter_by_id(del_id):
                                st.success(f"Voter record for ID '{del_id.strip()}' deleted.")
                                st.rerun()
                            else:
                                st.error("No matching voter found with this ID.")
                        else:
                            st.warning("Please enter an ID to delete.")

                with col_del2:
                    st.markdown("###### Option B: Select & Delete from Registry")
                    voter_options = {
                        f"{v['Full Name']} ({v['Unique Voter ID']})": v["Full Hash"]
                        for v in voters_records
                    }
                    selected_voter = st.selectbox("Select Enrolled Voter", list(voter_options.keys()))
                    if st.button("Purge Selected Voter"):
                        target_hash = voter_options[selected_voter]
                        if delete_voter_by_hash(target_hash):
                            st.success(f"Voter '{selected_voter}' removed.")
                            st.rerun()
                        else:
                            st.error("Failed to delete the selected record.")
            else:
                st.info("No voters currently enrolled in the database.")
    else:
        st.warning("Enter valid administrator credentials in the sidebar to access management controls.")