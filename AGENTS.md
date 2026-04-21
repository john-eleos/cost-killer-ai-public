# Cost-Killer AI Project Rules

## 🏗️ Architecture
- **Pattern:** Feature-based modularity.
- **Backend:** FastAPI with LiteLLM for universal routing.
- **Frontend:** Next.js (TypeScript) + Tailwind CSS.
- **Discovery:** Model list is dynamically sourced and self-qualified via telemetry.
- **Caching:** Semantic caching enabled via LiteLLM (local memory, upgradable to Redis).

## 🛡️ Security
- **Credentials:** NEVER commit `.env` or `usage_log.jsonl`.
- **Whitelisting:** Only use models from TRUSTED_PROVIDERS (Anthropic, OpenAI, Google, Meta, Mistral, DeepSeek, Alibaba).
- **Hardening:** Tier 1 tasks (Code, Strategy) MUST use verified top-tier models (Claude 3.5 Sonnet or GPT-4o).

## 📊 Reporting & Operations
- **Hourly Ledger:** Background process pushes real-time usage to Notion Team Inbox.
- **Email Report:** Twice-daily (12h interval) summary to the Boss.
- **Self-Qualification:** Models are ranked based on Latency-per-Token and Success Rate from logs.

## 🧠 Continuous Improvement (Friday v5.0 Strategy)
- Implement **Cascading Reasoning Loops**.
- Adopt **Model Context Protocol (MCP)** for cross-service connectivity.
- Shift to **DeepSeek V3.2** for high-efficiency Tier 2 tasks.
- Build **Unit Economics Dashboard** for user-level cost analysis.
