# Developer Tooling: Reading local .env files and generating safe, value-sanitized .env.example templates

import os

def generate_env_example(env_file_path=".env", output_file_path=".env.example"):
    """
    Parses a local .env configuration file, retains key names and comments,
    and replaces sensitive values with standardized placeholders.
    """
    print("--- Developer Tools: .env.example Template Generator ---")
    print(f"Target Environment Source: '{env_file_path}'\n")
    
    if not os.path.exists(env_file_path):
        # Generate a mock .env file if none exists for testing
        print(f" '{env_file_path}' not found. Creating a sample .env file for demonstration...")
        sample_content = (
            "# Database Credentials\n"
            "DB_HOST=127.0.0.1\n"
            "DB_PORT=5432\n"
            "DB_PASSWORD=SuperSecretPass123!\n\n"
            "# API Keys\n"
            "GITHUB_TOKEN=ghp_1234567890abcdef\n"
            "OPENAI_API_KEY=sk-proj-999888777666\n"
        )
        with open(env_file_path, "w", encoding="utf-8") as f:
            f.write(sample_content)
            
    example_lines = []
    processed_keys_count = 0
    
    with open(env_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        stripped_line = line.strip()
        
        # Preserve empty lines and comment lines
        if not stripped_line or stripped_line.startswith("#"):
            example_lines.append(line)
            continue
            
        # Parse KEY=VALUE configuration lines
        if "=" in stripped_line:
            key, _ = stripped_line.split("=", 1)
            key = key.strip()
            # Replace value with a standardized placeholder based on the key name
            placeholder_val = f"your_{key.lower()}_here"
            example_lines.append(f"{key}={placeholder_val}\n")
            processed_keys_count += 1
            print(f" Sanitized key: {key} -> {placeholder_val}")
            
    # Write sanitized content to .env.example
    with open(output_file_path, "w", encoding="utf-8") as out_f:
        out_f.writelines(example_lines)
        
    print("\nTemplate Generation Report:")
    print(f" Sanitized Keys Count : {processed_keys_count}")
    print(f" Exported Template    : '{output_file_path}'\n")
    return True

if __name__ == "__main__":
    generate_env_example()