#!/bin/bash
# Setup script for SWE-bench benchmark environment

set -e

echo "Setting up SWE-bench benchmark environment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Error: docker is required"; exit 1; }

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install SWE-bench
echo "Installing SWE-bench..."
cd swe-bench
pip install -e .
cd ..

# Install additional dependencies
echo "Installing additional dependencies..."
pip install rich datasets anthropic

echo "✓ Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run a sample benchmark:"
echo "  python run_swebench.py --config vanilla --sample 10 --output results/sample_vanilla"
