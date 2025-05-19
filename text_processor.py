import spacy
import re
import logging
from config import settings
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    azure_endpoint=settings.azure_openai_endpoint
)

def enhance_with_ai(job_desc: str, cv_text: str) -> str:
    """Dynamically enhance resume based on job description"""
    enhancement_prompt = f"""Analyze this job description and resume to create a tailored version and 
    Transform this resume to match the job requirements WITHOUT including the job description:
    
Job Description Requirements:
{job_desc[:3000]}

Resume Content:
{cv_text[:3000]}

Instructions:
1. Identify 5-7 key requirements from the job description
2. Match resume content to these requirements using actual experience
3. Prioritize technical skills mentioned in the JD
4. Add metrics/achievements where possible
5. Maintain original information but enhance relevance
6. Format sections by relevance to JD
7. Preserve contact information (anonymize if needed)
8. Remove any job description text
9. Focus only on candidate experience
10. Never mention "job description" in output
11. Maintain original contact info format

Output Format:
- Contact Info at top
- Summary highlighting JD-matched experience
- Skills section mirroring JD requirements
- Experience entries reordered by relevance
- Education/certifications at bottom"""

    try:
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[{
                "role": "system",
                "content": "You are a professional resume optimization system. Match candidate experience to job requirements."
            }, {
                "role": "user",
                "content": enhancement_prompt
            }],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"AI enhancement failed: {str(e)}")
        return cv_text
    
def preprocess_text(text: str) -> str:
    """Clean text while preserving structure"""
    text = re.sub(r'\b\w*@\w*\.\w*\b', '[EMAIL]', text)
    text = re.sub(r'http\S+', '[URL]', text)
    text = re.sub(r'\d{10,}', '[PHONE]', text)
    return text