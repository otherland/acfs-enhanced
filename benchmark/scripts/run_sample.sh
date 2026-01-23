#!/bin/bash
# Run a quick sample benchmark (10 tasks) to validate setup

set -e

source venv/bin/activate

echo "Running sample benchmark (10 tasks)..."
echo ""

# Run vanilla sample
echo "=== Running vanilla configuration ==="
python run_swebench.py \
  --config vanilla \
  --sample 10 \
  --output results/sample_vanilla \
  --timeout 300

echo ""
echo "=== Running acfs-enhanced configuration ==="
python run_swebench.py \
  --config acfs_enhanced \
  --sample 10 \
  --output results/sample_acfs \
  --timeout 300

echo ""
echo "=== Analyzing results ==="
python analyze_results.py \
  --vanilla results/sample_vanilla \
  --acfs results/sample_acfs \
  --output results/sample_comparison.md

echo ""
echo "✓ Sample benchmark complete!"
echo "View results: cat results/sample_comparison.md"
