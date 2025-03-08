import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import re

nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    # Remove sensitive information
    text = re.sub(r'\b\w*@\w*\.\w*\b', '', text)  # emails
    text = re.sub(r'http\S+', '', text)  # URLs
    text = re.sub(r'\d{10,}', '', text)  # phone numbers
    
    # Remove names and entities using NER
    doc = nlp(text)
    anonymized_text = []
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'GPE', 'LOC']:
            anonymized_text.append('[REDACTED]')
        else:
            anonymized_text.append(ent.text)
    text = ' '.join(anonymized_text)
    
    # Basic preprocessing
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text