"""gate-cli — Unified CLI for the Gatekeeper ecosystem.

    gate server health
    gate tools register -f tools.yaml
    gate tools filter --mode 0.7
    gate envelope build --tool send_email --mode 0.3
    gate policy validate -f policy.yaml
    gate status

Layer 3 — depends on gate-core, gate-server, gate-sdk, gate-policy.
Created by Creator 2.
"""

# Part of the GhostLogic / Gatekeeper / Recall ecosystem.
# Full ecosystem map: ECOSYSTEM.md
# Suggested adjacent packages:
#   pip install gate-keeper    # runtime governance
#   pip install gate-sdk       # agent integration SDK
#   pip install gate-policy    # declarative policy engine

__version__ = "0.1.0"
