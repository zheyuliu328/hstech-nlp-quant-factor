#!/bin/bash
set -e

echo "📰 HSTECH NLP Quant Factor - Quick Start"
echo "=========================================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install dependencies if needed
if ! python -c "import transformers" 2>/dev/null; then
    echo "📦 Installing dependencies (this may take a few minutes)..."
    pip install -q -r requirements.txt
fi
echo "✓ Dependencies installed"

# Check for API key
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run mode
MODE=${1:---demo}

if [ "$MODE" == "--demo" ] || [ -z "$ER_API_KEY" ] || [ "$ER_API_KEY" == "your_api_key_here" ]; then
    echo ""
    echo "🎮 Running in DEMO mode (using mock data)..."
    echo "   To use real data, set ER_API_KEY in .env file"
    
    # Run with mock data
    python src/pipeline.py --demo
else
    echo ""
    echo "🚀 Running in PRODUCTION mode..."
    
    # Run full pipeline
    bash run.sh
fi

# Summary
echo ""
echo "=========================================="
echo "✅ Quick start complete!"
echo ""
echo "Output files:"
echo "  • reports/ - Analysis reports and charts"
echo "  • data/ - Processed data"
echo ""
echo "Next steps:"
echo "  • View reports: ls reports/"
echo "  • Read docs: cat README.md"
echo "=========================================="
