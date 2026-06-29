import streamlit as st
import requests
import tempfile
import os

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Insurance Adjuster", layout="wide")
st.title("AI Insurance Adjuster")
st.markdown("Upload a fire/smoke damage image and optionally describe the incident.")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    description = st.text_area("Incident description (optional)", placeholder="Describe what happened...")
    material = st.selectbox(
        "Damage type for cost estimation",
        ["fire_damage_repair", "drywall", "flooring_wood", "roofing_shingle", "smoke_cleanup", "paint_interior"],
    )
    analyze_btn = st.button("Analyze Damage", type="primary")

with col2:
    if uploaded and analyze_btn:
        with st.spinner("Analyzing..."):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            try:
                with open(tmp_path, "rb") as f:
                    resp = requests.post(
                        f"{API_URL}/analyze",
                        files={"image": (uploaded.name, f, uploaded.type)},
                        data={"description": description, "material": material},
                        timeout=120,
                    )
            finally:
                os.unlink(tmp_path)

        if resp.status_code == 200:
            result = resp.json()
            da = result["damage_assessment"]
            fa = result["fraud_analysis"]
            ce = result["cost_estimate"]

            tabs = st.tabs(["Damage Assessment", "Fraud Analysis", "Cost Estimate"])

            with tabs[0]:
                st.subheader("Damage Assessment")
                st.metric("Detected Fire Areas", len(da["fire_detections"]))
                st.metric("Detected Smoke Areas", len(da["smoke_detections"]))
                st.metric("Estimated Area (m²)", f"{da['damaged_area_m2']:.2f}")
                if da["other_objects"]:
                    st.write("Other objects detected:")
                    for obj in da["other_objects"][:10]:
                        st.caption(f"- {obj['label']} ({obj['confidence']:.0%})")

            with tabs[1]:
                st.subheader("Fraud Analysis")
                score = fa["risk_score"]
                color = "red" if score > 0.6 else "orange" if score > 0.3 else "green"
                st.markdown(f"### Risk Score: <span style='color:{color}'>{score:.1%}</span>", unsafe_allow_html=True)
                st.metric("Total Flags", fa["total_flags"])
                st.metric("High Severity Flags", fa["high_severity_count"])
                for flag in fa["flags"]:
                    sev_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    st.write(f"{sev_icon.get(flag['severity'], '⚪')} **{flag['type'].replace('_', ' ').title()}** — {flag['message']}")
                    st.progress(flag["confidence"] / 100)

            with tabs[2]:
                if ce:
                    st.subheader("Cost Estimate")
                    st.metric("Material Cost", f"€{ce['material_cost']:.2f}")
                    st.metric("Labor Cost", f"€{ce['labor_cost']:.2f}")
                    st.metric("Total Estimated", f"€{ce['total_estimated']:.2f}")
                    st.caption(f"Category: {ce['category']} | Area: {ce['area_m2']:.2f} m²")
                else:
                    st.info("No damage detected; cost estimate not available.")
        else:
            st.error(f"Analysis failed: {resp.status_code} - {resp.text}")
    elif uploaded:
        st.image(uploaded, use_container_width=True)

with st.expander("About this project"):
    st.markdown("""
    **AI Insurance Adjuster** — Master project combining computer vision and fraud detection for insurance claims.
    - **Engine A**: Fire/smoke detection → damage measurement → cost estimation
    - **Engine B**: Burn pattern analysis → text/image inconsistency → red flag scoring
    """)
