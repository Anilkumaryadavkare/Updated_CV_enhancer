from collections import defaultdict
from cv_parser import parse_cv
from text_processor import preprocess_text, enhance_with_ai
from ranking_system import rank_candidates
from bias_detector import BiasDetector
import os

def parse_resume_sections(enhanced_text: str) -> dict:
    """Improved dynamic section parsing"""
    sections = defaultdict(list)
    current_section = 'contact'
    
    for line in enhanced_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Detect section headers
        if line.startswith('**') and line.endswith('**'):
            current_section = line[2:-2].lower().replace(' ', '_')
            continue
            
        # Structure content
        if line.startswith('- '):
            line = f"<li>{line[2:].strip()}</li>"
        elif ':' in line:
            parts = line.split(':', 1)
            line = f"<strong>{parts[0]}:</strong>{parts[1]}"
            
        sections[current_section].append(line)

    return sections

def main(jd_path: str, cv_paths: list) -> dict:
    results = {'enhanced_resumes': [], 'analysis': {}}
    bias_detector = BiasDetector()
    
    try:
        with open(jd_path, 'r', encoding='utf-8') as f:
            job_desc = preprocess_text(f.read())
    except Exception as e:
        print(f"Job description error: {str(e)}")
        return results

    cv_names = []
    cv_texts = []
    
    for cv_path in cv_paths:
        try:
            raw_text = parse_cv(cv_path)
            clean_text = preprocess_text(raw_text)
            
            # AI Enhancement with error fallback
            try:
                enhanced = enhance_with_ai(job_desc, clean_text)
            except Exception as ai_error:
                print(f"AI enhancement failed: {str(ai_error)}")
                enhanced = clean_text  # Fallback to original text
                
            # Section parsing
            sections = parse_resume_sections(enhanced)
            
            # Ranking calculation
            jd_match = 0.0
            if cv_names and cv_texts:
                rankings = rank_candidates(job_desc, cv_names, cv_texts)
                if rankings:
                    jd_match = rankings[-1][1]

            results['enhanced_resumes'].append({
                'raw': enhanced,
                'sections': sections,
                'analysis': {
                    'bias_score': bias_detector.get_bias_score(clean_text),
                    'jd_match': jd_match
                }
            })
            
            cv_names.append(os.path.basename(cv_path))
            cv_texts.append(clean_text)

        except Exception as e:
            print(f"CV processing failed: {cv_path} - {str(e)}")

    return results  

if __name__ == "__main__":
    sample_jd = "sample_data/job_description.txt"
    sample_cvs = [f"sample_data/{f}" for f in os.listdir("sample_data") if f.startswith('cv')]
    print(main(sample_jd, sample_cvs))