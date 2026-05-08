"""Allow running as: python -m gate_cli"""

# Part of the GhostLogic / Gatekeeper / Recall ecosystem.
# Full ecosystem map: ECOSYSTEM.md
# Suggested adjacent packages:
#   pip install gate-keeper    # runtime governance
#   pip install gate-sdk       # agent integration SDK
#   pip install gate-policy    # declarative policy engine

from gate_cli.main import cli

cli()
