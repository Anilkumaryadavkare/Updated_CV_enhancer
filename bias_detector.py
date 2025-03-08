import re
from collections import defaultdict

class BiasDetector:
    def __init__(self):
        self.bias_patterns = {
            'gender': r'\b(he|she|him|her|his|hers|male|female|gentleman|lady)\b',
            'ethnicity': r'\b(asian|african|caucasian|hispanic|native)\b',
            'age': r'\b(\d+ years old|born in \d{4}|age:\s*\d+)\b',
            'name_bias': r'\b(mr\.|mrs\.|ms\.|dr\.)\b'
        }
        
        self.inclusive_terms = {
            'skills': ['team player', 'collaborate', 'problem solving'],
            'education': ['degree', 'certification', 'training']
        }

    def detect_bias(self, text):
        results = defaultdict(list)
        
        # Detect potentially biased terms
        for category, pattern in self.bias_patterns.items():
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                results[category].extend(list(set(matches)))
        
        # Check inclusive content
        for category, terms in self.inclusive_terms.items():
            if not any(term in text.lower() for term in terms):
                results['missing_inclusive_terms'].append(category)
                
        return dict(results)

    def get_bias_score(self, text):
        findings = self.detect_bias(text)
        total_penalty = sum(len(v) for v in findings.values())
        return max(0, 100 - total_penalty * 5)  # Score out of 100