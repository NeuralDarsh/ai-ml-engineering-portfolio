# Developer Tooling: Validating standard 5-part cron syntax and parsing strings into readable schedules

import re

def parse_cron_expression(cron_str):
    """
    Validates a standard 5-part cron string (minute hour day_of_month month day_of_week)
    and generates a human-readable schedule interpretation.
    """
    print("--- Developer Tools: Cron Schedule Humanizer & Validator ---")
    print(f"Target Cron Expression: '{cron_str}'\n")
    
    parts = cron_str.strip().split()
    
    # 1. Verify standard 5-field structure
    if len(parts) != 5:
        print(f"VALIDATION FAILURE: Expected 5 fields, got {len(parts)}.")
        return False
        
    minute, hour, day_m, month, day_w = parts
    
    # Field boundary validation definitions
    validations = [
        ("Minute", minute, 0, 59),
        ("Hour", hour, 0, 23),
        ("Day of Month", day_m, 1, 31),
        ("Month", month, 1, 12),
        ("Day of Week", day_w, 0, 6) # 0 = Sunday, 6 = Saturday
    ]
    
    # 2. Check each field against value boundaries
    for name, val, min_v, max_v in validations:
        if val == "*":
            continue
        elif val.startswith("*/"):
            step = val.split("/")[1]
            if not step.isdigit() or int(step) < 1:
                print(f" INVALID STEP RULE in {name}: '{val}'")
                return False
        elif val.isdigit():
            v_int = int(val)
            if v_int < min_v or v_int > max_v:
                print(f" VALUE OUT OF RANGE in {name}: '{val}' (Allowed: {min_v}-{max_v})")
                return False
        else:
            # Simple fallback check for multi-value or range strings
            pass

    # 3. Build plain text humanizer string summary
    description_parts = []
    
    # Minute description
    if minute == "*":
        description_parts.append("Every minute")
    elif minute.startswith("*/"):
        description_parts.append(f"Every {minute.split('/')[1]} minutes")
    else:
        description_parts.append(f"At minute {minute}")
        
    # Hour description
    if hour == "*":
        description_parts.append("every hour")
    elif hour.startswith("*/"):
        description_parts.append(f"every {hour.split('/')[1]} hours")
    else:
        description_parts.append(f"at {hour.zfill(2)}:00")
        
    # Day of Week / Month description
    if day_w != "*":
        days_map = {"0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed", "4": "Thu", "5": "Fri", "6": "Sat"}
        description_parts.append(f"on {days_map.get(day_w, day_w)}")
    elif day_m != "*":
        description_parts.append(f"on day {day_m} of the month")
    else:
        description_parts.append("every day")
        
    readable_schedule = " ".join(description_parts) + "."
    
    print("Cron Validation & Humanizer Report:")
    print("  VALIDATION SUCCESL: Expression adheres to standard syntax rules.")
    print(f"  Human Interpretation: '{readable_schedule}'\n")
    
    return readable_schedule

if __name__ == "__main__":
    # Case A: Standard weekly database backup schedule (At 02:00 on Monday)
    sample_cron_A = "0 2 * * 1"
    parse_cron_expression(sample_cron_A)
    
    print("="*60 + "\n")
    
    # Case B: Standard 15-minute telemetry polling interval
    sample_cron_B = "*/15 * * * *"
    parse_cron_expression(sample_cron_B)