#!/usr/bin/env bash
# Sentinel-Gate AI: Ubuntu Environment Setup Script

set -e

echo "Updating system packages and installing prerequisites..."
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    cmake \
    g++ \
    git \
    curl

echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt pybind11

echo "Building C++20 Zero-Copy Pattern Engine..."
cd cpp_engine
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
cd ../..

echo "Setup completed successfully! Run 'source .venv/bin/activate' and start the server with 'python3 -m uvicorn sentinel_gate.backend.main:app'."
