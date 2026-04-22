from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import litellm
from litellm import completion
from litellm.caching import Cache
import os
import re
import time
import json
import collections
from api.discovery import ModelDiscovery

app = FastAPI(title="Cost-Killer AI v5.0 (Agentic Infrastructure)", version="5.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Discovery & Caching
discovery = ModelDiscovery()
DISCOVERED_MODELS = discovery.get_qualified_models()

# Redis Caching (Semantic cache via litellm)
try:
    litellm.cache = Cache(type="redis", host="localhost", port=6379)
except:
    print("Redis not found, falling back to local memory cache.")
    litellm.cache = Cache(type="local")

def refresh_model_qualification():
    """Background task to self-qualify models based on fresh logs."""
    global DISCOVERED_MODELS
    DISCOVERED_MODELS = discovery.get_qualified_models()
    print(f"--- Models Self-Qualified at {time.ctime()} ---")

# User Database & Rate Limiting State
USERS_DB = {
    "USER_PRIMARY": {"credits": 100.0, "role": "owner", "tier": "unlimited"},
    "TRIAL_123": {"credits": 5.0, "role": "trial", "tier": "basic"},
}
REQUEST_HISTORY = collections.defaultdict(list)

class RateLimiter:
    @staticmethod
    def check(key: str, limit_per_min: int = 10):
        now = time.time()
        REQUEST_HISTORY[key] = [t for t in REQUEST_HISTORY[key] if now - t < 60]
        if len(REQUEST_HISTORY[key]) >= limit_per_min:
            return False
        REQUEST_HISTORY[key].append(now)
        return True

def deduct_credits(key: str, cost: float):
    if key in USERS_DB:
        USERS_DB[key]["credits"] -= cost
        return USERS_DB[key]["credits"]
    return 0

def compress_context_v2(prompt: str) -> str:
    compressed = re.sub(r'\s+', ' ', prompt).strip()
    if len(compressed) > 100000:
        head = compressed[:30000]
        tail = compressed[-70000:]
        compressed = head + "\n...[CONTENT COMPRESSED]...\n" + tail
    return compressed

def get_optimal_model(prompt: str) -> tuple:
    prompt_lower = prompt.lower()
    
    # 1. Tier 1: High-Reasoning
    tier_1_keywords = ["write code", "fix bug", "architect", "deep dive", "analyze code", "security audit", "swarm", "sub-agent"]
    if any(k in prompt_lower for k in tier_1_keywords) or "```" in prompt:
        for model in DISCOVERED_MODELS:
            if "kimi-k2.6" in model["full_id"] and model.get("self_qualified_score", 0) > 90:
                return (model["full_id"], 0.024)
        return ("claude-3-5-sonnet-20240620", 0.00)
        
    # 2. Tier 2: Mid-Reasoning
    remote_models = sorted([m for m in DISCOVERED_MODELS if m.get("type") == "remote"], 
                           key=lambda x: x.get("self_qualified_score", 0), reverse=True)
    
    if len(prompt) > 4000 or "summarize" in prompt_lower:
        if len(prompt) > 500000:
            for deal in remote_models:
                if "llama-4" in deal["full_id"]:
                    return (deal["full_id"], 0.01)
                    
        for deal in remote_models:
            if "deepseek" in deal["full_id"] and deal.get("self_qualified_score", 0) > 85:
                return (deal["full_id"], 0.04)
        return ("gemini/gemini-1.5-flash", 0.035)
        
    # 3. Tier 3: Utility/Bulk
    local_qualified = sorted([m for m in DISCOVERED_MODELS if m.get("type") == "local"], 
                             key=lambda x: x.get("self_qualified_score", 0), reverse=True)
    
    if local_qualified and local_qualified[0].get("self_qualified_score", 0) > 70:
        return (local_qualified[0]["full_id"], 0.051)
    
    return ("groq/llama-3.3-70b-versatile", 0.05)

@app.post("/api/chat")
async def chat_completions(request: Request, background_tasks: BackgroundTasks):
    try:
        if time.time() % 60 < 5: 
            background_tasks.add_task(refresh_model_qualification)

        data = await request.json()
        license_key = data.get("license_key", "GUEST")

        if license_key not in USERS_DB or USERS_DB[license_key]["credits"] <= 0:
             raise HTTPException(status_code=403, detail="Insufficient credits or invalid key.")

        if not RateLimiter.check(license_key):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait 60s.")

        messages = data.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages")
        
        last_msg = messages[-1]["content"]
        if any(w in last_msg.lower() for w in ["billing", "production release", "deploy to prod"]):
            return JSONResponse(status_code=402, content={"error": "HITL_REQUIRED", "detail": "Action requires Human-in-the-Loop approval."})
        
        compressed_msg = compress_context_v2(last_msg)
        messages[-1]["content"] = compressed_msg
        
        target_model, savings = get_optimal_model(compressed_msg)
        
        start_time = time.time()
        litellm_kwargs = {k: v for k, v in data.items() if k not in ["model", "messages", "caching", "license_key"]}
        
        try:
            response = completion(
                model=target_model,
                messages=messages,
                caching=True,
                **litellm_kwargs
            )
        except Exception as api_err:
            raise HTTPException(status_code=502, detail=f"Upstream Provider Error: {str(api_err)}")

        end_time = time.time()
        latency = round(end_time - start_time, 3)
        cache_hit = getattr(response, '_hidden_params', {}).get("cache_hit", False)
        
        if cache_hit:
            savings += 0.05
            target_model = f"SEMANTIC_CACHE_HIT ({target_model})"

        out_tokens = response.usage.completion_tokens if (response.usage and hasattr(response.usage, 'completion_tokens')) else 0
        fee = 0.001 + (out_tokens * 0.000001)
        remaining = deduct_credits(license_key, fee)

        try:
            log_entry = {
                "timestamp": time.time(),
                "user": license_key,
                "model": target_model,
                "tokens": response.usage.total_tokens if response.usage else 0,
                "savings": savings,
                "cache_hit": cache_hit,
                "latency": latency,
                "fee": fee
            }
            with open("usage_log.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except: pass

        response_message = response.choices[0].message
        response_content = {
            "content": response_message.content,
            "metadata": {
                "model": target_model,
                "savings": f"${savings:.4f}",
                "cache": "HIT" if cache_hit else "MISS",
                "credits_remaining": f"${remaining:.4f}",
                "latency": f"{latency}s",
                "unit_economics_fee": f"${fee:.4f}"
            }
        }
        
        if hasattr(response_message, "tool_calls") and response_message.tool_calls:
            response_content["tool_calls"] = [
                {"id": t.id, "type": t.type, "function": {"name": t.function.name, "arguments": t.function.arguments}}
                for t in response_message.tool_calls
            ]

        return JSONResponse(content=response_content)

    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"error": he.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Internal Server Error: {str(e)}"})

@app.get("/api/admin/metrics")
async def get_metrics():
    return {
        "users_online": len(REQUEST_HISTORY), 
        "discovered_models": len(DISCOVERED_MODELS),
        "version": "5.2.0"
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "product": "Cost-Killer AI Agentic", "version": "5.2.0"}
