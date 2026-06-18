# Processing Japanese text strings to isolate grammatical particle tokens for AI training data

def analyze_japanese_particles(text_sentence):
    """
    Scans a Japanese text string to detect and classify grammatical particles.
    Essential preprocessing logic for localized NLP text classification models.
    """
    print("---  NLP Japanese Text Preprocessor (自然言語処理) ---")
    print(f"Input Text: {text_sentence}\n")
    
    # 1. Define standard Japanese N5 grammatical particles
    particles_to_track = {
        "は": "Topic Marker (wa)",
        "が": "Subject Marker (ga)",
        "を": "Object Marker (o)",
        "に": "Direction/Time Marker (ni)"
    }
    
    analysis_report = []
    
    # 2. String parsing logic to isolate tokens
    for particle, description in particles_to_track.items():
        count = text_sentence.count(particle)
        if count > 0:
            analysis_report.append({
                "particle": particle,
                "type": description,
                "occurrences": count
            })
            
    # 3. Output formatting for the data pipeline
    print("Particle Token Extraction Report:")
    if not analysis_report:
        print("  No primary particles detected in the target string.")
    else:
        for item in analysis_report:
            print(f"  🔹 Particle: {item['particle']} | Function: {item['type']:<22} | Found: {item['occurrences']} time(s)")
            
    return analysis_report

if __name__ == "__main__":
    # Sample sentence: "I study Python programming at university."
    # 私は大学でPythonプログラミングを勉強します。
    sample_nlp_string = "私は大学でPythonプログラミングを勉強します。"
    
    analyze_japanese_particles(sample_nlp_string)