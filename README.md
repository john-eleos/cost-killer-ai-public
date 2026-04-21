# 🚀 Cost-Killer AI: The Universal Agentic Gateway

**Stop paying the "Intelligence Tax."** Cost-Killer AI is a world-class, model-agnostic API gateway that slashes LLM inference costs by 80-95% while maintaining or improving quality.

Inspired by the patterns used in OpenClaw and Hermes, this gateway transitions you from **Reactive Routing** to **Agentic Infrastructure**.

---

## 🔥 Key Features

- **🧠 Agentic Cascading Logic**: Automatically tiers tasks. Code and complex reasoning go to Claude 3.5 or Kimi K2.6. Simple classification and formatting go to your **Local Hardware**.
- **🌐 Active Discovery**: On install, the gateway scans your computer for **Ollama**, **LM Studio**, and **HuggingFace** caches. It prioritizes the silicon you already own.
- **⚡ Semantic Caching**: Intercepts repeating queries for **0ms latency** and **$0.00 cost**.
- **🛠️ MCP / Tool Calling Bridge**: Full support for OpenAI/Anthropic tool schemas. Forward tool calls from your agent frameworks through our gateway.
- **📈 Self-Qualifying Models**: Ranks models based on real-world telemetry (success rate, latency-per-token) from your own logs, not just popularity.
- **💎 Monetization Ready**: Built-in license key and credit-based billing system. 

---

## 🛠️ Quick Local Setup

Run this command to install the gateway on your machine:

```bash
git clone https://github.com/john-eleos/cost-killer-ai-public.git
cd cost-killer-ai-public
chmod +x setup.sh && ./setup.sh
```

### Setup Requirements:
- Python 3.9+
- Node.js (for Dashboard)
- (Optional) Ollama or LM Studio for $0 routing.

---

## 💻 Usage

### 1. Start the Gateway
```bash
uvicorn api.main:app --port 8000
```

### 2. Connect Your App
Replace your OpenAI Base URL with your local gateway:
```python
import openai
client = openai.OpenAI(
    base_url="http://localhost:8000/v1", # Route through Cost-Killer
    api_key="your_license_key"           # Use your CK license key
)
```

### 3. Use the CLI Client
We provide a standalone client for quick testing:
```bash
python3 scripts/client.py "Write a rust function for a blockchain node"
```

---

## 🛡️ Security & Privacy
- **Zero-Data Leakage**: Your API keys and logs never leave your server.
- **Trusted Whitelist**: Only routes to verified, high-performance organizations.
- **HITL Gates**: Built-in Human-in-the-Loop protection for high-stakes actions.

## 🌍 Become Part of the Infrastructure
Cost-Killer AI is designed to be the backbone of your AI operations. Build on top of it, fork it, or deploy it to Vercel to share with your team.

Built by **Gemini CLI** | Powered by **LiteLLM**.
