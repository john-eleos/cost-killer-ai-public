#!/bin/bash

echo "🚀 Initializing Cost-Killer AI: Local Setup..."

# 1. Check Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 not found. Please install it to continue."
    exit
fi

# 2. Install Dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt -q

# 3. Create .env if missing
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cat <<EOF > .env
# --- Cost-Killer AI Environment ---
# Add your API keys below to enable remote routing.
# Local models (Ollama/LM Studio) are automatically detected.

GROQ_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
EOF
    echo "✅ .env created. Please add your keys there."
fi

# 4. Initialize Model Discovery
echo "🔍 Scanning for local models..."
python3 -c "from api.discovery import ModelDiscovery; d = ModelDiscovery(); d.initialize_system()"

echo "------------------------------------------------"
echo "✅ Setup Complete!"
echo "------------------------------------------------"
echo "1. Run 'uvicorn api.main:app --reload' to start the gateway."
echo "2. Open 'http://localhost:8000/api/health' to verify."
echo "3. Use 'python3 scripts/client.py \"Your prompt\"' to test."
echo "------------------------------------------------"
