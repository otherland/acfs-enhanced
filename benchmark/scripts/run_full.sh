#!/bin/bash
# Run full SWE-bench Lite benchmark (300 tasks)
# WARNING: This may take 2-4 hours and cost ~$900 in API calls

set -e

source venv/bin/activate

# Confirmation
echo "WARNING: You are about to run the full SWE-bench Lite benchmark."
echo ""
echo "Expected:"
echo "  - Runtime: 2-4 hours"
echo "  - API cost: ~$900 (300 tasks × 2 configs × ~500K tokens/task)"
echo "  - Docker containers: 600+ (300 tasks × 2 configs)"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo ""
echo "Starting full benchmark at $TIMESTAMP"
echo ""

# Run vanilla
echo "=== Running vanilla configuration ==="
python run_swebench.py \
  --config vanilla \
  --output results/full_${TIMESTAMP}_vanilla \
  --timeout 600

echo ""
echo "=== Running acfs-enhanced configuration ==="
python run_swebench.py \
  --config acfs_enhanced \
  --output results/full_${TIMESTAMP}_acfs \
  --timeout 600

echo ""
echo "=== Analyzing results ==="
python analyze_results.py \
  --vanilla results/full_${TIMESTAMP}_vanilla \
  --acfs results/full_${TIMESTAMP}_acfs \
  --output results/full_${TIMESTAMP}_comparison.md

echo ""
echo "✓ Full benchmark complete!"
echo "Results: results/full_${TIMESTAMP}_comparison.md"
