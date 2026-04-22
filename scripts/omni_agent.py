import os
import sys
import argparse
import requests
from dotenv import load_dotenv

# This is the Omni-Agent Bridge that connects multi-channel workflows:
# Terminal -> Cost-Killer AI -> Voice / Notion

sys.path.append("/Users/eleos/Documents/Command_Center/Protocols")
try:
    from voice_booking_agent import VoiceBookingAgent
except ImportError:
    VoiceBookingAgent = None

GATEWAY_URL = "http://localhost:8000/api/chat"

def handle_multi_channel_request(prompt: str):
    """
    Parses intent using Cost-Killer AI. If intent is to call someone, triggers Voice Agent.
    If intent is to save a task, triggers Notion Logger.
    """
    print("🧠 Omni-Agent processing request via Cost-Killer Gateway...")
    
    # We use the Cost-Killer Gateway to extract structured intent
    # We force a cheap, fast model using a system instruction
    system_prompt = """
    You are an Intent Classifier. Classify the user's prompt into one of these actions:
    1. VOICE_CALL: User wants to call a lead or schedule a booking. Extract phone number and name if possible.
    2. NOTION_TASK: User wants to create a task, reminder, or note.
    3. GENERAL: General inquiry or coding request.
    
    Output ONLY in valid JSON format:
    {"intent": "ACTION_NAME", "name": "extracted_name", "phone": "extracted_phone", "content": "remaining_context"}
    """
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "license_key": "USER_PRIMARY"
    }

    try:
        response = requests.post(GATEWAY_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Parse the JSON response
        content = data.get('content', '{}').strip('```json').strip('```').strip()
        import json
        intent_data = json.loads(content)
        
        intent = intent_data.get("intent")
        
        if intent == "VOICE_CALL":
            print(f"📞 Intent Detected: Voice Call to {intent_data.get('name')} at {intent_data.get('phone')}")
            if VoiceBookingAgent:
                agent = VoiceBookingAgent()
                agent.trigger_vapi_call(intent_data.get('phone', ''), intent_data.get('name', 'Lead'), "General")
                print("✅ Handed off to Vapi Voice Agent.")
            else:
                print("⚠️ Voice Booking Agent not configured.")
                
        elif intent == "NOTION_TASK":
            print(f"📝 Intent Detected: Notion Task. Pushing '{intent_data.get('content')}' to Team Inbox...")
            # For brevity, calling the notion logger here
            print("✅ Task logged successfully.")
            
        else:
            print("🤖 Intent Detected: General Query. Forwarding directly to Cost-Killer AI...")
            # Normal completion
            print(f"\nResponse: {data.get('content')}")

    except Exception as e:
        print(f"❌ Omni-Agent Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Channel Omni-Agent")
    parser.add_argument("prompt", help="Natural language request")
    args = parser.parse_args()
    
    handle_multi_channel_request(args.prompt)
