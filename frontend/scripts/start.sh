#!/bin/bash
# Start NexlifyCorp Frontend Development Server

set -e

echo "Starting NexlifyCorp Frontend..."
echo ""

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    bun install
fi

# Check for LangGraph API URL
if [ -z "$NEXT_PUBLIC_LANGGRAPH_API_URL" ]; then
    echo "Warning: NEXT_PUBLIC_LANGGRAPH_API_URL not set. Defaulting to http://localhost:2024"
fi

echo ""
echo "Starting development server..."
echo "Frontend: http://localhost:3000"
echo "Note: Make sure LangGraph API is running on port 2024"
echo ""

bun run dev