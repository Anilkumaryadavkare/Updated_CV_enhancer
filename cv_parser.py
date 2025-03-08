import PyPDF2
from docx import Document
import os

def parse_cv(file_path):
    text = ""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = " ".join([page.extract_text() for page in reader.pages])
        elif ext == '.docx':
            doc = Document(file_path)
            text = " ".join([para.text for para in doc.paragraphs])
        else:  # txt file
            with open(file_path, 'r') as f:
                text = f.read()
    except Exception as e:
        print(f"Error parsing {file_path}: {str(e)}")
    
    return text