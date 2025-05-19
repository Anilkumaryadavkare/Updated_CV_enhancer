# streamlit_app.py  ✔ fixed
import streamlit as st
import requests
import os
import json               # ← already present, left here for clarity

API = os.getenv("CV_API", "http://localhost:8001")

st.title("AI‑powered Resume Enhancer")

# ────────────────────────────────────────────────────────────────────────────
# ① Upload & analyse CV(s)
# ────────────────────────────────────────────────────────────────────────────
cv_file = st.file_uploader(
    "Upload CV (pdf/docx/txt)",
    type=["pdf", "docx", "txt"]
)
job_desc = st.text_area("Paste job description")

if st.button("Enhance") and cv_file and job_desc:
    files = [("cvs", (cv_file.name, cv_file, cv_file.type))]
    data = {"job_desc": job_desc}

    with st.spinner("Analyzing..."):
        try:
            r = requests.post(f"{API}/analyze", data=data, files=files, timeout=120)
            r.raise_for_status()
            res = r.json()

            if res.get("enhanced_resumes"):
                st.session_state["resume"] = res["enhanced_resumes"][0]
                st.success("Analysis complete! Scroll down to edit.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# ────────────────────────────────────────────────────────────────────────────
# ② Review / edit & download PDF
# ────────────────────────────────────────────────────────────────────────────
if "resume" in st.session_state:
    st.subheader("Review/Edit Enhanced Resume")
    edited = st.text_area(
        "Edit your resume:",
        value=st.session_state["resume"].get("raw", ""),
        height=500
    )

    # persist edits to sections if user changed the raw text (optional)
    st.session_state["resume"]["raw"] = edited

    template_id = st.selectbox(
        "Choose template",
        options=["clean-blue", "modern-grey"]
    )

    if st.button("Generate PDF"):
        with st.spinner("Generating PDF..."):
            try:
                # 🚩 NEW: send JSON, not plain text
                enhanced_content = json.dumps({
                    "sections": st.session_state["resume"]["sections"]
                    # you could also send the whole object:
                    # **json.dumps(st.session_state["resume"])**
                })

                r = requests.post(
                    f"{API}/generate_resume",
                    json={
                        "content": enhanced_content,
                        "template_id": template_id
                    },
                    timeout=120
                )
                r.raise_for_status()

                st.download_button(
                    "Download PDF",
                    data=r.content,
                    file_name=f"resume_{template_id}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF generation failed: {str(e)}")
