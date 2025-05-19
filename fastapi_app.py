from fastapi import FastAPI, File, UploadFile, Form, Body, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile
import os
import io
import traceback
from pydantic import BaseModel
from main import main as analyze_cvs
from resume_generator import pdf_bytes

app = FastAPI(title="AK‑CV Analyzer")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeRequest(BaseModel):
    content: str
    template_id: str

@app.post("/analyze")
async def analyze(
    job_desc: str = Form(...),
    cvs: List[UploadFile] = File(...)
):
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # Validate inputs
            if not job_desc.strip():
                raise HTTPException(status_code=400, detail="Job description cannot be empty")
                
            if not cvs:
                raise HTTPException(status_code=400, detail="At least one CV required")

            # Save files
            jd_path = os.path.join(tmp, "jd.txt")
            with open(jd_path, "w", encoding="utf-8") as f:
                f.write(job_desc)

            cv_paths = []
            for i, cv in enumerate(cvs):
                ext = os.path.splitext(cv.filename)[1].lower()
                if ext not in ['.pdf', '.docx', '.txt']:
                    raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
                
                contents = await cv.read()
                cv_path = os.path.join(tmp, f"cv_{i}{ext}")
                with open(cv_path, "wb") as f:
                    f.write(contents)
                cv_paths.append(cv_path)

            # Process data
            results = analyze_cvs(jd_path, cv_paths)
            
            # Convert defaultdicts
            for resume in results["enhanced_resumes"]:
                if isinstance(resume.get('sections'), dict):
                    resume['sections'] = dict(resume['sections'])
            
            return results
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(e)}"}
        )

@app.post("/generate_resume")
async def generate_resume(request: ResumeRequest):
    try:
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="Empty content")
            
        return StreamingResponse(
            io.BytesIO(pdf_bytes(request.content, request.template_id)),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=resume_{request.template_id}.pdf"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"PDF generation failed: {str(e)}"}
        )