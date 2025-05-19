import os, tempfile
from flask import Flask, request, jsonify, Response
from main import main as analyze_cvs
from resume_generator import pdf_bytes

app = Flask(__name__)

# ---------- /analyze (unchanged) ----------
@app.route("/analyze", methods=["POST"])
def analyze():
    job_desc = request.files["job_desc"]
    cvs      = request.files.getlist("cvs")

    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, "job_description.txt")
        job_desc.save(jd_path)

        cv_paths = []
        for i, cv in enumerate(cvs):
            cv_path = os.path.join(tmpdir, f"cv_{i}{os.path.splitext(cv.filename)[1]}")
            cv.save(cv_path)
            cv_paths.append(cv_path)

        results = analyze_cvs(jd_path, cv_paths)
    return jsonify(results)


# ---------- NEW: /generate_resume ----------
@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    """
    Expects JSON:
        { "content": "<raw text>", "template_id": "clean-blue" }
    Returns: PDF file.
    """
    data        = request.get_json(force=True)
    raw_text    = data.get("content", "")
    template_id = data.get("template_id", "clean-blue")

    try:
        pdf = pdf_bytes(raw_text, template_id)
        return Response(
            pdf,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=resume_{template_id}.pdf"
            },
        )
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    app.run(host="0.0.0.0", port=port)
