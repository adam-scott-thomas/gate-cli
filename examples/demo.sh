#!/usr/bin/env bash
# gate-cli demo — full workflow against a running gate-server
#
# Prerequisites:
#   pip install -e ../gate-server
#   python -m gate_server &
#   pip install -e .
#
set -euo pipefail

echo "=== Gate CLI Demo ==="
echo ""

echo "1. Server health"
gate server health
echo ""

echo "2. Register tools from YAML"
gate tools register -f examples/tools.yaml
echo ""

echo "3. List registered tools"
gate tools list
echo ""

echo "4. Filter at normal mode (0.2)"
gate tools filter --mode 0.2
echo ""

echo "5. Filter at crisis mode (0.9)"
gate tools filter --mode 0.9
echo ""

echo "6. Validate read_logs at crisis"
gate tools validate read_logs --mode 0.9
echo ""

echo "7. Validate deploy_production at crisis"
gate tools validate deploy_production --mode 0.9
echo ""

echo "8. Build envelope for read_logs"
gate envelope build --tool read_logs --mode 0.3
echo ""

echo "9. Build envelope, save to file, verify"
gate -o json envelope build --tool read_logs --mode 0.3 > /tmp/envelope.json
gate envelope verify -f /tmp/envelope.json
echo ""

echo "10. Export OpenAI-compatible tools"
gate tools export --mode 0.5
echo ""

echo "11. Mode history"
gate server history
echo ""

echo "12. Full status"
gate status
echo ""

echo "13. Local mode (no server)"
gate --local tools filter --mode 0.9 -f examples/tools.yaml
echo ""

echo "=== Demo complete ==="
