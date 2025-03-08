from flask import Flask, request, jsonify
from main import main as analyze_cvs
import tempfile
import os

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get files from request
    job_desc = request.files['job_desc']
    cvs = request.files.getlist('cvs')
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save job description
        jd_path = os.path.join(tmpdir, 'job_description.txt')
        job_desc.save(jd_path)
        
        # Save CVs
        cv_paths = []
        for i, cv in enumerate(cvs):
            cv_path = os.path.join(tmpdir, f'cv_{i}{os.path.splitext(cv.filename)[1]}')
            cv.save(cv_path)
            cv_paths.append(cv_path)
        
        # Run analysis
        results = analyze_cvs(jd_path, cv_paths)
        
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)