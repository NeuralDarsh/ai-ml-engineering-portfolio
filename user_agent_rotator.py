# Developer Tooling: Generating dynamic HTTP headers to simulate diverse web browsers and prevent bot blocks

import random
import urllib.request
import urllib.error

class UserAgentRotator:
    """
    Manages a pool of realistic browser User-Agent strings to dynamically mask
    outgoing HTTP network requests during scraping or web monitoring tasks.
    """
    def __init__(self):
        # Realistic User-Agent browser strings (Chrome, Firefox, Safari, Edge across Windows, macOS, Linux)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ]

    def get_random_header(self):
        """Returns a formatted HTTP header dictionary containing a randomly selected User-Agent."""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def send_masked_request(self, target_url):
        """Wraps a target URL inside a masked HTTP request with rotated headers."""
        headers = self.get_random_header()
        print(f"Sending Request to: {target_url}")
        print(f" Applied User-Agent: {headers['User-Agent'][:60]}...")
        
        req = urllib.request.Request(target_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=4.0) as response:
                status_code = response.getcode()
                print(f" Connection Successful | Status Code: {status_code}\n")
                return True
        except urllib.error.HTTPError as err:
            print(f"HTTP Error: {err.code}\n")
            return False
        except Exception as err:
            print(f"Connection Failed: {err}\n")
            return False

if __name__ == "__main__":
    print("---  Developer Tools: User-Agent Header Rotator ---")
    
    rotator = UserAgentRotator()
    
    # Simulate making 3 continuous requests with rotated browser signatures
    test_target = "https://httpbin.org/user-agent"
    
    for i in range(1, 4):
        print(f"[Request Sequence #{i}]")
        rotator.send_masked_request(test_target)