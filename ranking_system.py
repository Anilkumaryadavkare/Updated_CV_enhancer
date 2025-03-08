from sklearn.feature_extraction.text import TfidfVectorizer  # Add this import
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def rank_candidates(job_desc, cvs, cv_texts):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([job_desc] + cv_texts)
    
    job_vector = vectors[0]
    cv_vectors = vectors[1:]
    
    similarities = cosine_similarity(job_vector, cv_vectors)
    ranked_indices = np.argsort(similarities[0])[::-1]
    
    return [(cvs[i], similarities[0][i]) for i in ranked_indices]