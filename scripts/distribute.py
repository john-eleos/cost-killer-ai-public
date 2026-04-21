import os
import sys

# Append the path so we can use the existing email engine
sys.path.append("/Users/eleos/Documents/Command_Center/Protocols")

try:
    from email_engine import send_email
except ImportError:
    print("Email engine not found. Ensure you run this from the correct environment.")
    sys.exit(1)

GATEWAY_URL = "https://web-zeta-umber-70.vercel.app"
TESTER_EMAILS = ["ajuwonayodeji.a@gmail.com"]

email_body = f"""Hello!

You have been exclusively selected to participate in the Private Beta of Cost-Killer AI v5.0 (Agentic Infrastructure).

Cost-Killer AI is a model-agnostic API gateway that acts as a "Cost-First Firewall" for large language models. It automatically analyzes the Reasoning Intensity of your prompts, compresses tokens, and dynamically routes your requests to the most cost-effective and capable models on the market (Claude 3.5, Gemini 1.5 Flash, DeepSeek V3.2, or Llama 3.3).

This architecture allows developers to cut their AI API inference bills by up to 80-95% while maintaining high-quality output.

HOW TO TEST IT:
To test the API, you can use our lightweight Python client. Save the code below to a file named `cost_killer_local.py` and run it from your terminal.

==================================================
import sys
import requests
import argparse

GATEWAY_URL = "{GATEWAY_URL}/api/chat"

def main():
    parser = argparse.ArgumentParser(description="Cost-Killer AI: Local Client")
    parser.add_argument("prompt", help="The prompt to send to the router")
    parser.add_argument("--key", help="Your License Key", default="TRIAL_123")
    args = parser.parse_args()

    print(f"--- Routing to {{GATEWAY_URL}} ---")
    payload = {{
        "messages": [{{"role": "user", "content": args.prompt}}],
        "license_key": args.key
    }}
    
    try:
        response = requests.post(GATEWAY_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"\\n[Model Used: {{data.get('metadata', {{}}).get('model', 'Unknown')}}]")
        print(f"[Estimated Savings: {{data.get('metadata', {{}}).get('savings', '$0.00')}}]")
        print("-" * 40)
        print(data.get('content', 'No content returned'))
        print("-" * 40)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Billing Error: {{e.response.json().get('detail', 'Forbidden')}}")
        else:
            print(f"Network Error: {{e}}")

if __name__ == "__main__":
    main()
==================================================

Example usage:
python3 cost_killer_local.py "Can you summarize the benefits of open-source models?"

FEEDBACK REQUEST:
We want to be the most effective AI tool for developers worldwide. Please reply directly to this email with your feedback, bug reports, and any feature requests!

Best regards,
The Eleos Technologies Team
"""

for email in TESTER_EMAILS:
    print(f"Sending beta invite to {email}...")
    try:
        send_email(
            to_email=email,
            subject="🚀 Invitation: Cost-Killer AI v5.0 Private Beta",
            body=email_body
        )
        print(f"✅ Sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send to {email}: {e}")
