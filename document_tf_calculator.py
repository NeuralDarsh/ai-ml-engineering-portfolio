# Implementing text mining preprocessing token weights for NLP search models

def calculate_term_frequency(document_text, target_keywords):
    """
    Tokenizes raw text to calculate the mathematical Term Frequency (TF).
    Formula: TF = (Count of Keyword in Doc) / (Total Words in Doc)
    """
    print("---  NLP Data Pipeline: Term Frequency Matrix ---")
    
    # 1. Clean and tokenize the input document text string
    cleaned_text = document_text.lower().replace(".", "").replace(",", "")
    words_list = cleaned_text.split()
    total_word_count = len(words_list)
    
    print(f"Target Document Length: {total_word_count} tokens\n")
    tf_matrix = {}
    
    # 2. Algorithmic frequency count and mathematical normalization
    for keyword in target_keywords:
        lower_keyword = keyword.lower()
        keyword_count = words_list.count(lower_keyword)
        
        # Calculate TF score ratio metric
        tf_score = keyword_count / total_word_count if total_word_count > 0 else 0.0
        tf_matrix[keyword] = round(tf_score, 4)
        
        print(f"  Keyword: '{keyword:<12}' | Found: {keyword_count} time(s) | TF Score: {tf_matrix[keyword]}")
        
    print("\n---  Extraction Processing Complete ---")
    return tf_matrix

if __name__ == "__main__":
    # Simulated engineering candidate background paragraph profile
    sample_resume_profile = (
        "Darshan is an engineer studying Artificial Intelligence and Machine Learning. "
        "He builds production AI pipelines, manages hardware IoT arrays daily, and writes "
        "optimized Python code to deploy deep learning automation systems internationally."
    )
    
    # Selected professional terminology keywords to evaluate
    industry_keywords = ["Artificial", "Python", "IoT", "Japan", "Automation"]
    
    calculate_term_frequency(sample_resume_profile, industry_keywords)