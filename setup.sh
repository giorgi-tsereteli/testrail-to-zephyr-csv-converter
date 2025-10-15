#!/bin/bash
# Setup script for TestRail to Jira CSV Converter

set -e  # Exit on any error

echo "🚀 Setting up TestRail to Jira CSV Converter..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Test installation
echo "🧪 Testing installation..."
python3 -c "from src.transformer import CSVTransformer; print('✅ Transformer module loaded successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Setup completed successfully!"
    echo ""
    echo "🎉 You're ready to use the CSV converter!"
    echo ""
    echo "Quick start:"
    echo "  1. Test with sample data: ./test.sh"
    echo "  2. Replace testrail_export.csv with your data"
    echo "  3. Run transformation: ./test.sh"
    echo ""
    echo "📖 See README.md for detailed usage instructions."
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi