import sys
import requests
import argparse
import os

# The deployed Vercel URL (replace with your real one once deployed)
GATEWAY_URL = os.getenv("COST_KILLER_URL", "https://cost-killer-ai.vercel.app/api/chat")

def main():
    parser = argparse.ArgumentParser(description="Cost-Killer AI: Local Client")
    parser.add_argument("prompt", help="The prompt to send to the router")
    parser.add_argument("--key", help="Your Cost-Killer License Key", default=os.getenv("COST_KILLER_KEY"))
    args = parser.parse_args()

    if not args.key:
        print("Error: No License Key provided. Get one at: https://cost-killer-ai.vercel.app/buy")
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
        
        print(f"\n[Model: {data['model_used']}]")
        print(f"[Savings: ${data['savings']:.4f}]")
        print("-" * 20)
        print(data['content'])
        print("-" * 20)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Billing Error: {e.response.json()['detail']}")
        else:
            print(f"Network Error: {e}")

if __name__ == "__main__":
    main()
