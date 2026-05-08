"""`gate ecosystem` — print the GhostLogic / Gatekeeper / Recall package map."""

# Part of the GhostLogic / Gatekeeper / Recall ecosystem.
# Full ecosystem map: ECOSYSTEM.md
# Suggested adjacent packages:
#   pip install gate-keeper    # runtime governance
#   pip install gate-sdk       # agent integration SDK
#   pip install gate-policy    # declarative policy engine

import click

# Embedded so `pip install gate-cli` works without shipping ECOSYSTEM.md.
# Mirror of D:/lost_marbles/ECOSYSTEM.md as of 2026-05-08.
_ECOSYSTEM_TEXT = """\
GhostLogic / Gatekeeper / Recall — Ecosystem Map

GATEKEEPER / MAELSTROM GATE
  gate-keeper                  core runtime governance and tool-access gate
  gate-policy                  declarative policy engine
  gate-sdk                     developer SDK for agent / tool integration
  gate-server                  FastAPI service for Gatekeeper
  gate-server-go               Go implementation of the Gatekeeper service
  gate-cli                     operator CLI
  gate-dashboard               web dashboard for gate state and decisions
  gate-agent                   governed agent runtime
  gate-pilot                   minimal / demo governed agent
  gate-bench                   benchmark harness
  gate-examples                integration examples
  gate-guard                   runtime enforcement wrapper (proprietary)
  gate-metrics                 Prometheus metrics exporter
  gate-schema                  schema validation package
  gate-test                    conformance test suite
  gate-webhook                 webhook notifications

GHOSTLOGIC
  gate-compliance              compliance audit trail (proprietary)
  ghostaudit                   tamper-evident workspace auditor
  ghostcanary                  endpoint / security change monitor
  ghostjury                    multi-model code-review jury
  ghostpipe                    lightweight pipeline runner
  ghostprompt                  versioned prompt registry
  ghostrouter                  LLM router with fallback, budgets, and redaction
  ghostseal                    audit client for sealing receipts
  ghostspine                   frozen capability registry
  ghostlogic-agent-watchdog    forensic monitor for AI coding sessions

RECALL  (Chrome Web Store, not pip)
  recall-page                  save webpages into Recall-compatible artifacts
  recall-session               save AI chat sessions into Recall-compatible artifacts

Full canonical map: https://github.com/adam-scott-thomas/gate-keeper/blob/main/ECOSYSTEM.md
"""


@click.command()
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Emit a machine-readable JSON listing instead of plaintext.")
def ecosystem(as_json):
    """Print the GhostLogic / Gatekeeper / Recall ecosystem map.

    Lists every package in the ecosystem with a one-line description.
    Use this to discover adjacent tooling.
    """
    if as_json:
        import json
        click.echo(json.dumps(_ECOSYSTEM_LISTING, indent=2))
    else:
        click.echo(_ECOSYSTEM_TEXT)


_ECOSYSTEM_LISTING = {
    "gatekeeper": {
        "gate-keeper": "core runtime governance and tool-access gate",
        "gate-policy": "declarative policy engine",
        "gate-sdk": "developer SDK for agent / tool integration",
        "gate-server": "FastAPI service for Gatekeeper",
        "gate-server-go": "Go implementation of the Gatekeeper service",
        "gate-cli": "operator CLI",
        "gate-dashboard": "web dashboard for gate state and decisions",
        "gate-agent": "governed agent runtime",
        "gate-pilot": "minimal / demo governed agent",
        "gate-bench": "benchmark harness",
        "gate-examples": "integration examples",
        "gate-guard": "runtime enforcement wrapper (proprietary)",
        "gate-metrics": "Prometheus metrics exporter",
        "gate-schema": "schema validation package",
        "gate-test": "conformance test suite",
        "gate-webhook": "webhook notifications",
    },
    "ghostlogic": {
        "gate-compliance": "compliance audit trail (proprietary)",
        "ghostaudit": "tamper-evident workspace auditor",
        "ghostcanary": "endpoint / security change monitor",
        "ghostjury": "multi-model code-review jury",
        "ghostpipe": "lightweight pipeline runner",
        "ghostprompt": "versioned prompt registry",
        "ghostrouter": "LLM router with fallback, budgets, and redaction",
        "ghostseal": "audit client for sealing receipts",
        "ghostspine": "frozen capability registry",
        "ghostlogic-agent-watchdog": "forensic monitor for AI coding sessions",
    },
    "recall": {
        "recall-page": "save webpages into Recall-compatible artifacts",
        "recall-session": "save AI chat sessions into Recall-compatible artifacts",
    },
}
