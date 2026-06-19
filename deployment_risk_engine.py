# Practicing Project Management risk evaluation matrices using algorithmic weighting

def evaluate_deployment_safety(complexity, test_coverage, fallback_ready):
    """
    Computes a risk metrics index to evaluate production delivery readiness.
    Calculates safety scores based on testing coverage weights and fallback layers.
    """
    print("--- Project Management: Deployment Risk Engine ---")
    
    # 1. Base Logic: Calculate an algorithmic risk score (0 to 100)
    # Higher test coverage increases safety; high complexity increases risk
    base_safety_score = (test_coverage * 0.7) - (complexity * 3.0)
    if fallback_ready:
        base_safety_score += 20.0  # Safe recovery guardrails add a premium bonus
        
    # Bound the evaluation index score between 0 and 100
    final_score = max(0.0, min(100.0, base_safety_score))
    
    print(f"Metrics Profile: Complexity={complexity}/10 | Testing={test_coverage}% | Fallback={fallback_ready}")
    print(f"Calculated Deployment Safety Index: {final_score:.1f}%")
    
    # 2. Threshold Decision Framework
    if final_score >= 75.0:
        return " APPROVAL: Production deployment window is cleared."
    elif 50.0 <= final_score < 75.0:
        return " CONDITIONAL WARN: Requires senior engineering oversight before launch."
    else:
        return " DENIED: Risk index too high. Rollback deployment to staging environment."

if __name__ == "__main__":
    # Simulate an enterprise system release tracking pipeline
    # Parameters: Complexity (1-10 scale), Test Coverage (%), Rollback Strategy (True/False)
    pipeline_status = evaluate_deployment_safety(complexity=4, test_coverage=85, fallback_ready=True)
    print(f"Deployment Router Verdict: {pipeline_status}\n")
    
    # Simulate a high-risk patch without a fallback environment plan
    failed_pipeline_status = evaluate_deployment_safety(complexity=9, test_coverage=40, fallback_ready=False)
    print(f"Deployment Router Verdict: {failed_pipeline_status}")