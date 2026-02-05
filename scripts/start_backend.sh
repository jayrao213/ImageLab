#!/bin/bash
# PhotoApp Backend Startup Script for Linux/Mac

echo "========================================"
echo "  PhotoApp FastAPI Backend"
echo "========================================"
echo ""

cd ../backend

echo "Checking Python installation..."
python3 --version
echo ""

echo "Installing/Updating dependencies..."
pip3 install -r requirements.txt
echo ""

echo "Starting FastAPI server..."
echo ""
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 main.py
