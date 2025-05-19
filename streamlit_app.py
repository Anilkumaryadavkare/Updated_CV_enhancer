import streamlit as st
import requests, os, json

API = os.getenv("CV_API", "http://localhost:8001")

st.title("AI‑powered Resume Enhancer")

# ── Upload & analyse ───────────────────────────────────────────
cv_file = st.file_uploader("Upload CV (pdf / docx / txt)",
                           type=["pdf", "docx", "txt"])
job_desc = st.text_area("Paste job description")

if st.button("Enhance") and cv_file and job_desc:
    with st.spinner("Analyzing…"):
        r = requests.post(f"{API}/analyze",
                          data={"job_desc": job_desc},
                          files=[("cvs", (cv_file.name, cv_file, cv_file.type))],
                          timeout=120)
        if r.ok and r.json().get("enhanced_resumes"):
            st.session_state["resume"] = r.json()["enhanced_resumes"][0]
            st.success("Done! Scroll down to review.")
        else:
            st.error(r.text or "Analysis failed")

# ── Review / choose template / download ───────────────────────
if "resume" in st.session_state:
    edited = st.text_area("Review & edit:",
                          value=st.session_state["resume"]["raw"],
                          height=500)
    st.session_state["resume"]["raw"] = edited

    template_id = st.selectbox("Choose template",
                               ["clean-blue", "modern-sleek"])

if st.button("Generate PDF"):
    with st.spinner("Generating PDF..."):
        try:
            resume_data = {
                "content": st.session_state["resume"]["raw"],
                "template_id": template_id
            }

            r = requests.post(f"{API}/generate_resume", json=resume_data, timeout=120)
            r.raise_for_status()

            st.download_button(
                "Download PDF",
                data=r.content,
                file_name=f"resume_{template_id}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")
