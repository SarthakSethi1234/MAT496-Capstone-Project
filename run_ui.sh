#!/bin/bash

# Simple script to run the Streamlit UI

echo "Starting Product Research Agent Web UI..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create a .env file with your API keys:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "TAVILY_API_KEY=your_key_here"
    echo ""
fi

# Run Streamlit
streamlit run web_ui.py
