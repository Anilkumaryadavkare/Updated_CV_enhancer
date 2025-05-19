from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def rank_candidates(job_desc: str, cvs: list, cv_texts: list) -> list:
    """Rank candidates based on job description similarity"""
    if not job_desc.strip():
        return [(cv, 0.0) for cv in cvs]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        vectors = vectorizer.fit_transform([job_desc] + cv_texts)
    except ValueError:
        return [(cv, 0.0) for cv in cvs]
    
    job_vector = vectors[0]
    cv_vectors = vectors[1:]
    
    similarities = cosine_similarity(job_vector, cv_vectors)
    ranked_indices = np.argsort(similarities[0])[::-1]
    
    return [(cvs[i], similarities[0][i]) for i in ranked_indices]