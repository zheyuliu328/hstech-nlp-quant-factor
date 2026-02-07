#!/bin/bash
set -e

echo "📰 HSTECH NLP Quant Factor - Quick Start"
echo "=========================================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install dependencies if needed
if ! python -c "import pandas" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Check for API key
DEMO_MODE=true
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep ER_API_KEY | xargs 2>/dev/null || true)
    if [ -n "$ER_API_KEY" ] && [ "$ER_API_KEY" != "your_api_key_here" ]; then
        DEMO_MODE=false
    fi
fi

# Run pipeline
if [ "$DEMO_MODE" = true ]; then
    echo ""
    echo "🎮 Running in DEMO mode (using sample data)..."
    echo "   To use real data, set ER_API_KEY in .env file"
    echo ""
    
    python src/data_pipe_demo.py
    
    echo ""
    echo "📊 Generating demo report..."
    python -c "
import json
from pathlib import Path

# Load demo results
with open('reports/demo_sentiment_results.json') as f:
    data = json.load(f)

# Generate simple report
report = {
    'mode': 'DEMO',
    'articles_processed': len(data),
    'sentiment_distribution': {
        'positive': sum(1 for d in data if d['sentiment'] == 'positive'),
        'negative': sum(1 for d in data if d['sentiment'] == 'negative'),
        'neutral': sum(1 for d in data if d['sentiment'] == 'neutral')
    }
}

# Save report
Path('reports').mkdir(exist_ok=True)
with open('reports/quickstart_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('✓ Report saved to: reports/quickstart_report.json')
print(json.dumps(report, indent=2))
"
else
    echo ""
    echo "🚀 Running in PRODUCTION mode..."
    echo ""
    python src/data_pipe.py --symbols 0700.HK --recent_pages 1
fi

# Summary
echo ""
echo "=========================================="
echo "✅ Quick start complete!"
echo ""
echo "Output files:"
ls -lh reports/ 2>/dev/null || echo "  (No reports generated)"
echo ""
echo "Next steps:"
echo "  • View reports: cat reports/quickstart_report.json"
echo "  • Read docs: cat README.md"
echo "=========================================="
