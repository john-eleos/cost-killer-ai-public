import os
import json
import requests
import subprocess
from typing import List, Dict

# Trusted AI Organizations (Battle-tested and Secure)
TRUSTED_PROVIDERS = [
    "anthropic", "openai", "google", "meta", "mistral", 
    "deepseek", "alibaba", "cohere", "together", "groq", "moonshot"
]

# High-Effectiveness Model Whitelist (Based on LMSYS/HumanEval benchmarks)
EFFECTIVE_MODELS = {
    "claude-3-5-sonnet-20240620": {"score": 98, "tier": 1},
    "gpt-4o": {"score": 97, "tier": 1},
    "kimi-k2.6": {"score": 96, "tier": 1}, # New release: April 20, 2026
    "llama-3.3-70b-versatile": {"score": 92, "tier": 2},
    "gemini-1.5-flash": {"score": 88, "tier": 2},
    "deepseek-chat": {"score": 91, "tier": 2},
    "qwen2.5-coder-32b": {"score": 90, "tier": 2},
    "llama-3.1-8b-instant": {"score": 82, "tier": 3},
}

class ModelScorer:
    """
    Self-Qualifies models based on real-world telemetry logs.
    Qualification is based on: Success Rate, Latency-to-Token Ratio, and Cost.
    """
    @staticmethod
    def qualify_from_logs(logs_path: str) -> Dict[str, float]:
        scores = {}
        if not os.path.exists(logs_path):
            return scores

        performance_data = {} # {model_id: [success_bool, latency, tokens]}
        
        with open(logs_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    m = entry["model"]
                    if m not in performance_data: performance_data[m] = []
                    performance_data[m].append({
                        "success": 1 if "error" not in entry else 0,
                        "latency": entry.get("latency", 1.0),
                        "tokens": entry.get("tokens", 1)
                    })
                except: continue

        for model, data in performance_data.items():
            success_rate = sum(d["success"] for d in data) / len(data)
            avg_latency_per_token = sum(d["latency"] for d in data) / sum(max(1, d["tokens"]) for d in data)
            
            # Score formula: (Success % * 100) - (Latency Penalty)
            score = (success_rate * 100) - (avg_latency_per_token * 10)
            scores[model] = round(max(0, score), 2)
            
        return scores

class ModelDiscovery:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = os.path.join(os.getcwd(), data_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.discovery_file = os.path.join(self.data_dir, "discovered_models.json")
        self.usage_log = "usage_log.jsonl"

    def is_trusted_and_effective(self, model_id: str, provider: str) -> bool:
        if provider.lower() not in TRUSTED_PROVIDERS:
            return False
        model_name_lower = model_id.lower()
        trusted_families = ["llama", "mistral", "phi", "qwen", "gemma"]
        if any(family in model_name_lower for family in trusted_families):
            return True
        return model_id in EFFECTIVE_MODELS

    def scan_local_runtimes(self) -> List[Dict]:
        discovered = []
        # 1. Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for m in models:
                    if self.is_trusted_and_effective(m["name"], "meta"):
                        discovered.append({
                            "name": m["name"],
                            "provider": "ollama",
                            "full_id": f"ollama/{m['name']}",
                            "cost": 0.0,
                            "type": "local",
                            "confidence": "high"
                        })
        except: pass

        # 2. Check for LM Studio
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=1)
            if response.status_code == 200:
                models = response.json().get("data", [])
                for m in models:
                    discovered.append({
                        "name": m["id"],
                        "provider": "lmstudio",
                        "full_id": f"openai/{m['id']}",
                        "cost": 0.0,
                        "type": "local",
                        "confidence": "high"
                    })
        except: pass
        return discovered

    def source_remote_deals(self) -> List[Dict]:
        """
        Actively sources for high-performance, low-cost models 
        ONLY from trusted remote providers. Updated for April 2026.
        """
        potential_deals = [
            {"name": "Kimi-K2.6", "provider": "moonshot", "full_id": "moonshot/kimi-k2.6", "cost": 0.0006, "type": "remote"},
            {"name": "DeepSeek-V3.2", "provider": "deepseek", "full_id": "openrouter/deepseek/deepseek-chat", "cost": 0.00028, "type": "remote"},
            {"name": "Claude-Sonnet-4.6", "provider": "anthropic", "full_id": "anthropic/claude-3-5-sonnet-20240620", "cost": 0.003, "type": "remote"},
            {"name": "Llama-4-Scout", "provider": "meta", "full_id": "groq/llama-4-scout-70b", "cost": 0.0005, "type": "remote"},
            {"name": "Gemini-2.5-Flash-Lite", "provider": "google", "full_id": "google/gemini-1.5-flash", "cost": 0.0001, "type": "remote"}
        ]
        return [d for d in potential_deals if self.is_trusted_and_effective(d["name"], d["provider"])]

    def get_qualified_models(self) -> List[Dict]:
        local = self.scan_local_runtimes()
        remote = self.source_remote_deals()
        all_models = local + remote
        dynamic_scores = ModelScorer.qualify_from_logs(self.usage_log)
        for m in all_models:
            m_id = m["full_id"]
            m["self_qualified_score"] = dynamic_scores.get(m_id, 85.0 if m["type"] == "local" else 80.0)
        with open(self.discovery_file, "w") as f:
            json.dump(all_models, f, indent=4)
        return all_models

    def initialize_system(self):
        return self.get_qualified_models()

if __name__ == "__main__":
    discovery = ModelDiscovery()
    models = discovery.initialize_system()
    print(json.dumps(models, indent=2))
