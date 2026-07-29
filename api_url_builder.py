# Developer Tooling: Safely encoding and serializing dynamic query dictionaries into valid URL strings

from urllib.parse import urlencode, urljoin

def build_api_endpoint_url(base_url, endpoint_path, query_params=None):
    """
    Combines a base URL, endpoint path, and query parameter dictionary
    into a safely encoded, production-ready web URL.
    """
    print("--- Developer Tools: API URL Builder & Query Serializer ---")
    
    # 1. Ensure clean base path join without double slashes
    full_path = urljoin(base_url if base_url.endswith('/') else base_url + '/', endpoint_path.lstrip('/'))
    
    if not query_params:
        print(f"Built Clean Base URL: {full_path}")
        return full_path
        
    # 2. Serialize query parameters dictionary into percent-encoded URL string
    # doseq=True handles list elements naturally (e.g., tags=['ai', 'python'] -> tags=ai&tags=python)
    encoded_query_string = urlencode(query_params, doseq=True)
    
    # 3. Construct final complete URL string
    final_url = f"{full_path}?{encoded_query_string}"
    
    print(" URL Serialization Execution Report:")
    print(f"Ingested Base Path : {base_url}")
    print(f"Endpoint Subpath   : {endpoint_path}")
    print(f"Raw Query Dict     : {query_params}")
    print(f"Serialized API URL : {final_url}\n")
    
    return final_url

if __name__ == "__main__":
    base_endpoint = "https://api.github.com"
    target_route = "/search/repositories"
    
    # Query parameters containing spaces, special symbols, and list objects
    search_parameters = {
        "q": "applied ai systems language:python",
        "sort": "stars",
        "order": "desc",
        "per_page": 10,
        "tags": ["portfolio", "automation"]
    }
    
    build_api_endpoint_url(base_endpoint, target_route, search_parameters)