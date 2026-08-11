# Software Engineering: Analyzing source code files to compute lines of code (LOC), blank lines, and comment ratios

import os

def profile_code_metrics(file_path):
    """
    Parses a source code file to calculate total lines, actual lines of code (LOC),
    blank lines, and comment line counts to compute documentation ratios.
    """
    print("--- Software Engineering: Source Code Metrics Profiler ---")
    print(f"Target Source File: '{file_path}'\n")

    if not os.path.exists(file_path):
        print(f" Error: Specified file path '{file_path}' does not exist.")
        return None

    total_lines = 0
    code_lines = 0
    comment_lines = 0
    blank_lines = 0

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            total_lines += 1
            stripped = line.strip()

            if not stripped:
                blank_lines += 1
            elif stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
                comment_lines += 1
            else:
                code_lines += 1

    # Calculate documentation ratio
    comment_ratio = (comment_lines / (code_lines + comment_lines) * 100) if (code_lines + comment_lines) > 0 else 0

    print("Source Code Metrics Report:")
    print("=" * 50)
    print(f" Total Lines       : {total_lines}")
    print(f" Lines of Code (LOC): {code_lines}")
    print(f" Comment Lines     : {comment_lines}")
    print(f" Blank Lines       : {blank_lines}")
    print(f" Comment Ratio     : {comment_ratio:.1f}%")
    print("=" * 50)

    if comment_ratio >= 15.0:
        print(" DOCUMENTATION VERDICT: Well-documented code module.\n")
    else:
        print("DOCUMENTATION VERDICT: Low comment density. Consider adding docstrings/comments.\n")

    return {
        "total": total_lines,
        "loc": code_lines,
        "comments": comment_lines,
        "blanks": blank_lines,
        "comment_ratio_pct": round(comment_ratio, 1)
    }

if __name__ == "__main__":
    # Profile today's script file itself as a live demonstration
    current_script = __file__
    profile_code_metrics(current_script)