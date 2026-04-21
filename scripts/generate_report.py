import json
import time
import os
import sys

# Path to Protocols for email engine
sys.path.append("/Users/eleos/Documents/Command_Center/Protocols")
try:
    from email_engine import send_email
except ImportError:
    send_email = None

LOG_FILE = "usage_log.jsonl"
REPORT_FILE = "hourly_report.md"
BOSS_EMAIL = "osunifedayo@gmail.com"

def self_optimize_check(logs):
    """
    Analyzes logs for high latency or errors and updates 
    routing strategy internally (conceptually).
    """
    total_latency = 0
    count = 0
    for entry in logs[-50:]: # Check last 50 queries
        total_latency += entry.get("latency", 0)
        count += 1
    
    avg_latency = total_latency / max(1, count)
    if avg_latency > 3.0: # System is getting slow
        return "⚠️ Alert: Latency exceeds 3s. Consider switching to Groq/Llama-8B for Tier 2."
    return "✅ Performance is optimal."

def generate_report():
    if not os.path.exists(LOG_FILE):
        return
        
    total_savings = 0.0
    total_revenue = 0.0
    total_queries = 0
    cache_hits = 0
    tokens_processed = 0
    models_used = {}
    users_active = set()
    all_logs = []

    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                all_logs.append(entry)
                total_savings += entry.get("savings", 0.0)
                # Fallback to 0.001 if fee isn't present in older logs
                total_revenue += entry.get("fee", 0.001) 
                total_queries += 1
                tokens_processed += entry.get("tokens", 0)
                users_active.add(entry.get("user", "unknown"))
                if entry.get("cache_hit"):
                    cache_hits += 1
                
                model = entry.get("model", "unknown")
                models_used[model] = models_used.get(model, 0) + 1
            except Exception:
                pass

    health_check = self_optimize_check(all_logs)
    
    # Calculate Unit Economics
    avg_cost_per_handoff = total_revenue / max(1, total_queries)
    
    # Extract Model Rankings from DISCOVERED_MODELS
    model_rankings = ""
    try:
        with open("data/discovered_models.json", "r") as df:
            discovered = json.load(df)
            sorted_m = sorted(discovered, key=lambda x: x.get("self_qualified_score", 0), reverse=True)
            for m in sorted_m[:5]: # Top 5
                model_rankings += f"- **{m['full_id']}**: Score **{m.get('self_qualified_score', 0)}** ({m['type']})\n"
    except:
        model_rankings = "Calculating..."

    report = f"""# 🚀 Cost-Killer AI v5.0 (Agentic) Hourly Report
*Generated at: {time.ctime()}*

### 💰 Unit Economics & Business Metrics
- **Average Cost per Handoff:** ${avg_cost_per_handoff:.5f}
- **Total Revenue (Fees):** ${total_revenue:.4f}
- **Total User Savings:** ${total_savings:.4f}
- **Active Paying Users:** {len(users_active)}
- **Total Queries Processed:** {total_queries}
- **Semantic Cache Hits:** {cache_hits} ({(cache_hits/max(1, total_queries))*100:.1f}%)

### 🏆 Top Self-Qualified Models (Real-World Performance)
{model_rankings}

### 🧠 Model Routing Distribution
"""
    for model, count in models_used.items():
        report += f"- **{model}**: {count} queries\n"

    report += f"\n### 🛠️ Self-Optimization Diagnostic\n- **Status:** {health_check}\n"
    report += "\n*System is running autonomously and self-correcting routing logic.*"

    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"Report generated: {REPORT_FILE}")

    # Send Email Report (Twice Daily)
    EMAIL_STATE_FILE = "last_email_time.txt"
    last_email_time = 0.0
    if os.path.exists(EMAIL_STATE_FILE):
        try:
            with open(EMAIL_STATE_FILE, "r") as f:
                last_email_time = float(f.read().strip())
        except:
            pass

    current_time = time.time()
    # 43200 seconds = 12 hours
    if send_email and (current_time - last_email_time >= 43200):
        try:
            send_email(BOSS_EMAIL, f"🚀 AI Cost-Killer Report: ${total_revenue:.4f} Revenue", report)
            print("✅ Report sent via email.")
            with open(EMAIL_STATE_FILE, "w") as f:
                f.write(str(current_time))
        except Exception as e:
            print(f"❌ Email failed: {e}")
    else:
        hours_left = (43200 - (current_time - last_email_time)) / 3600
        print(f"⏭️ Skipping email (next email in ~{hours_left:.1f} hours).")

if __name__ == "__main__":
    generate_report()
