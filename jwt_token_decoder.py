# Developer Tooling: Base64URL decoding JWT strings into readable header and payload JSON objects

import base64
import json
from datetime import datetime

def decode_jwt_token(jwt_string):
    """
    Splits a standard JWT string into Header, Payload, and Signature components,
    restores Base64URL padding, and formats payload claims.
    """
    print("--- Developer Tools: JWT Token Decoder & Parser ---")
    
    parts = jwt_string.strip().split(".")
    if len(parts) != 3:
        print(" INVALID JWT: Expected 3 dot-separated segments (Header.Payload.Signature).")
        return None
        
    def base64url_decode(segment):
        # Restore Base64 padding (length must be a multiple of 4)
        rem = len(segment) % 4
        if rem > 0:
            segment += "=" * (4 - rem)
        decoded_bytes = base64.urlsafe_b64decode(segment)
        return json.loads(decoded_bytes.decode("utf-8"))

    try:
        header = base64url_decode(parts[0])
        payload = base64url_decode(parts[1])
        
        print("Decoded JWT Token Structure:")
        print(f"Header  : {json.dumps(header)}")
        print(f"Payload : {json.dumps(payload, indent=4)}")
        
        # Convert standard epoch claims ('exp', 'iat') to human-readable timestamps
        if "exp" in payload:
            exp_date = datetime.fromtimestamp(payload["exp"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"Expiration Time (exp) : {exp_date}")
            
        if "iat" in payload:
            iat_date = datetime.fromtimestamp(payload["iat"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"Issued At Time (iat)  : {iat_date}")
            
        print("\nDECODE SUCCESSFUL: Token payload structure unpacked.")
        return {"header": header, "payload": payload}
        
    except Exception as err:
        print(f"DECODE ERROR: Failed to unpack token content ({err}).")
        return None

if __name__ == "__main__":
    # Simulated standard JWT token string (Header.Payload.Signature)
    sample_jwt = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJkYXJzaGFuX2RldiIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc4NTgxMTIwMCwiZXhwIjoxNzg1ODk3NjAwfQ."
        "SignatureComponentSample"
    )
    
    decode_jwt_token(sample_jwt)