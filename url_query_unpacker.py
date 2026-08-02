# Developer Tooling: Ingesting raw web URLs and unpacking query strings into clean dictionaries

from urllib.parse import urlparse, parse_qs, unquote
import json

def unpack_url_query_parameters(raw_url):
    """
    Parses a raw URL string, isolates path components, and unpacks
    percent-encoded query parameters into a normalized data dictionary.
    """
    print("---  Developer Tools: URL Query String Unpacker ---")
    print(f"Ingested Raw URL:\n  {raw_url}\n")
    
    # 1. Break the URL string into standard structural components
    parsed_url = urlparse(raw_url)
    
    # 2. Extract multi-value query dictionary (parse_qs converts keys into lists automatically)
    raw_query_dict = parse_qs(parsed_url.query)
    
    # 3. Clean up and normalize single-item vs multi-item query values
    unpacked_payload = {}
    for key, value_list in raw_query_dict.items():
        # Decodes percent-encoded characters (e.g., %20 -> space)
        decoded_values = [unquote(v) for v in value_list]
        
        # If the parameter appears only once, flatten it out of the list wrapper
        if len(decoded_values) == 1:
            unpacked_payload[key] = decoded_values[0]
        else:
            unpacked_payload[key] = decoded_values
            
    # 4. Construct a clean result object
    parsed_result = {
        "scheme": parsed_url.scheme,
        "hostname": parsed_url.netloc,
        "path": parsed_url.path,
        "query_parameters": unpacked_payload
    }
    
    print("Unpacked URL Payload Report:")
    print(f" Service Host : {parsed_result['hostname']}")
    print(f" Endpoint Path: {parsed_result['path']}")
    print(" Query Data   :")
    print(json.dumps(unpacked_payload, indent=4))
    print("\n")
    
    return parsed_result

if __name__ == "__main__":
    # Simulated inbound web URL with encoded spaces, filters, and list parameters
    sample_inbound_url = (
        "https://api.sentianalyze.pro/v2/search"
        "?q=machine%20learning%20models"
        "&category=nlp"
        "&tags=ai"
        "&tags=python"
        "&page=1"
        "&active=true"
    )
    
    unpack_url_query_parameters(sample_inbound_url)