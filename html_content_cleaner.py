# Data Engineering: Parsing raw web HTML strings, stripping markup noise, and extracting clean text

import re
import html

def extract_clean_text_from_html(raw_html_content):
    """
    Strips script tags, style blocks, and generic HTML tags from a raw web page string,
    decodes HTML entities, and normalizes spacing into clean plain text for AI pipelines.
    """
    print("--- Data Engineering: HTML Content Cleaner & Text Extractor ---")
    
    if not raw_html_content:
        print("Error: Provided HTML content is empty.")
        return ""
        
    # 1. Remove inline script and style elements completely (including internal content)
    cleaned_step1 = re.sub(r'<script.*?>.*?</script>', ' ', raw_html_content, flags=re.DOTALL | re.IGNORECASE)
    cleaned_step2 = re.sub(r'<style.*?>.*?</style>', ' ', cleaned_step1, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. Strip away all remaining generic HTML markup tags (<tag>)
    cleaned_step3 = re.sub(r'<.*?>', ' ', cleaned_step2)
    
    # 3. Decode standard HTML character entities (&amp; -> &, &lt; -> <, etc.)
    decoded_text = html.unescape(cleaned_step3)
    
    # 4. Collapse multi-space noise and redundant blank lines into clean text
    normalized_lines = [line.strip() for line in decoded_text.splitlines() if line.strip()]
    final_plain_text = "\n".join(normalized_lines)
    
    print("HTML Text Extraction Execution Report:")
    print(f"Raw Input Length   : {len(raw_html_content)} characters")
    print(f"Clean Output Length : {len(final_plain_text)} characters")
    print("------------------------------------------------------------")
    print(f"Extracted Clean Text Payload:\n{final_plain_text}")
    print("------------------------------------------------------------\n")
    
    return final_plain_text

if __name__ == "__main__":
    # Simulated raw web page HTML payload containing tags, styles, and entities
    sample_web_page_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SentiAnalyze Pro Overview</title>
        <style>
            body { background-color: #0d1117; color: #fff; }
            .header { font-size: 24px; }
        </style>
        <script>
            console.log("Initializing analytics tracking engine...");
        </script>
    </head>
    <body>
        <div class="container">
            <h1>SentiAnalyze Pro &amp; ML Architecture</h1>
            <p>Developing high-throughput sentiment analysis pipelines &lt;v2.1&gt; using Python.</p>
            <a href="https://github.com">View GitHub Portfolio</a>
        </div>
    </body>
    </html>
    """
    
    extract_clean_text_from_html(sample_web_page_html)