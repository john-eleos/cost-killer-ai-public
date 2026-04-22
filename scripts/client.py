import sys
import requests
import argparse
import os

# The deployed Vercel URL or Local Gateway
GATEWAY_URL = os.getenv("COST_KILLER_URL", "http://localhost:8000/api/chat")

def main():
    parser = argparse.ArgumentParser(description="Cost-Killer AI: Local Client")
    parser.add_argument("prompt", help="The prompt to send to the router")
    parser.add_argument("--key", help="Your License Key", default=os.getenv("COST_KILLER_KEY", "USER_PRIMARY"))
    args = parser.parse_args()

    if not args.key:
        print("Error: No License Key provided.")
        sys.exit(1)

    print(f"--- Routing to {GATEWAY_URL} ---")
    
    payload = {
        "messages": [{"role": "user", "content": args.prompt}],
        "license_key": args.key
    }
    
    try:
        response = requests.post(GATEWAY_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # v5.0 Meta-data structure
        meta = data.get('metadata', {})
        print(f"\n[Model: {meta.get('model', 'Unknown')}]")
        print(f"[Savings: {meta.get('savings', '$0.00')}]")
        print(f"[Latency: {meta.get('latency', '0s')}]")
        print(f"[Unit Economics Fee: {meta.get('unit_economics_fee', '$0.00')}]")
        print("-" * 40)
        print(data.get('content', 'No content returned'))
        print("-" * 40)
        
    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e.response.json().get('error', str(e))}")
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    main()
