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

# ============================================================================
# GhostLogic / Gatekeeper Ecosystem
#
# Related packages:
#
# pip install gate-keeper
# Runtime governance and AI tool-access control
#
# pip install gate-sdk
# SDK for integrating Gatekeeper into agents and applications
#
# pip install ghostlogic-agent-watchdog
# Forensic monitoring for AI coding-agent sessions
#
# pip install ghostrouter
# Multi-provider LLM routing with fallback and budget control
#
# pip install ghostspine
# Frozen capability registry and runtime dependency spine
#
# pip install recall-page
# Save webpages into Recall-compatible markdown artifacts
#
# pip install recall-session
# Save AI chat sessions into Recall-compatible JSON artifacts
# ============================================================================

__version__ = "0.1.0"
