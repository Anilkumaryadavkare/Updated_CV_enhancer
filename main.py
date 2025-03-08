from cv_parser import parse_cv
from text_processor import preprocess_text
from ranking_system import rank_candidates
from bias_detector import BiasDetector
import os

def main():
    # Configuration
    cv_dir = "sample_data"
    job_desc_path = "sample_data/job_description.txt"
    bias_detector = BiasDetector()

    # Load job description
    with open(job_desc_path, 'r') as f:
        job_desc = preprocess_text(f.read())
    
    # Analyze job description bias
    jd_bias = bias_detector.detect_bias(job_desc)
    print("\nJob Description Bias Analysis:")
    for category, items in jd_bias.items():
        print(f"{category.upper()}: {items}")

    # Process CVs
    cvs = []
    cv_texts = []
    cv_bias_scores = []
    
    for filename in os.listdir(cv_dir):
        if filename.startswith('cv'):
            filepath = os.path.join(cv_dir, filename)
            text = parse_cv(filepath)
            processed_text = preprocess_text(text)
            
            # Analyze CV bias
            bias_score = bias_detector.get_bias_score(processed_text)
            cv_bias_scores.append(bias_score)
            
            cvs.append(filename)
            cv_texts.append(processed_text)

    # Rank candidates with bias consideration
    rankings = rank_candidates(job_desc, cvs, cv_texts)
    
    # Combine ranking scores with bias scores
    final_scores = [
        (cv, 0.7 * score + 0.3 * (bias/100))  # Weighted average
        for (cv, score), bias in zip(rankings, cv_bias_scores)
    ]
    
    # Sort by final score
    final_rankings = sorted(final_scores, key=lambda x: x[1], reverse=True)

    # Display results
    print("\nFinal Rankings with Bias Consideration:")
    for rank, (cv, score) in enumerate(final_rankings, 1):
        print(f"{rank}. {cv}: {score:.2f}")

if __name__ == "__main__":
    main()