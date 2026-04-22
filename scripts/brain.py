import os
import time
import json
from typing import List, Dict

class LocalBrain:
    """
    World-Class Compounding Knowledge Engine.
    Allows users to ingest sources and build a persistent 'Brain' that 
    the router can query for zero-cost context.
    """
    def __init__(self, base_dir: str = "brain"):
        self.base_dir = base_dir
        self.wiki_dir = os.path.join(base_dir, "wiki")
        self.raw_dir = os.path.join(base_dir, "raw")
        self.log_file = os.path.join(self.wiki_dir, "log.md")
        self.index_file = os.path.join(self.wiki_dir, "index.md")
        
        self._initialize_structure()

    def _initialize_structure(self):
        folders = ["concepts", "entities", "sources", "synthesis"]
        for f in folders:
            os.makedirs(os.path.join(self.wiki_dir, f), exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("# 🧠 Brain Log\n\n## Timeline of Knowledge Ingestion\n")

    def ingest(self, source_path: str, summary: str, keywords: List[str]):
        """
        Permanently files knowledge into the Brain.
        """
        filename = os.path.basename(source_path)
        safe_name = filename.replace(".", "_")
        
        # 1. Create Source Page
        source_page = os.path.join(self.wiki_dir, "sources", f"{safe_name}.md")
        with open(source_page, "w") as f:
            f.write(f"# Source: {filename}\n\n## Summary\n{summary}\n\n## Concepts\n")
            for k in keywords:
                f.write(f"- [[{k}]]\n")

        # 2. Update Log
        with open(self.log_file, "a") as f:
            date_str = time.strftime('%Y-%m-%d')
            f.write(f"\n## [{date_str}] ingest | {filename}")

        print(f"✅ Knowledge Ingested: {source_page}")

    def query_context(self, prompt: str) -> str:
        """
        Searches the local brain for context before hitting an LLM.
        (Future: Implement local vector search here)
        """
        return "Local brain context searching... (v1.0)"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cost-Killer AI: Local Brain Engine")
    parser.add_argument("--ingest", help="Path to file to ingest")
    parser.add_argument("--summary", help="Brief summary of the knowledge")
    args = parser.parse_args()

    brain = LocalBrain()
    if args.ingest and args.summary:
        brain.ingest(args.ingest, args.summary, ["AI", "Infrastructure"])
    else:
        print("🧠 Local Brain is active. Use --ingest to add knowledge.")
