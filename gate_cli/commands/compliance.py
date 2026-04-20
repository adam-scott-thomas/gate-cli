"""Compliance subcommand for gate-cli -- run audit reports from the terminal.

Bridges gate-cli (Layer 3) with gate-compliance (Layer 2).
Requires gate-compliance installed.

STUB -- needs gate-cli's command registration system wired up.
Seeded by Creator 1 (gate-compliance), Loop 5.

Usage (once wired):
    gate compliance report
    gate compliance report --format json
    gate compliance report --since 24
    gate compliance stats
    gate compliance alerts
    gate compliance export --format splunk
"""
from __future__ import annotations


def register(subparsers) -> None:
    """Register the compliance subcommand with gate-cli's argument parser.

    An Improver should call this from gate_cli/main.py's argument setup.
    """
    parser = subparsers.add_parser("compliance", help="Run compliance reports and alerts")
    sub = parser.add_subparsers(dest="compliance_cmd")

    # gate compliance report
    report = sub.add_parser("report", help="Generate compliance report")
    report.add_argument("--format", choices=["text", "json", "csv"], default="text")
    report.add_argument("--since", type=float, help="Hours to look back")
    report.add_argument("--db", default="gate_audit.db", help="Audit database path")

    # gate compliance stats
    sub.add_parser("stats", help="Quick event counts")

    # gate compliance alerts
    sub.add_parser("alerts", help="Run compliance alert checks")

    # gate compliance export
    export = sub.add_parser("export", help="Export for SIEM")
    export.add_argument("--format", choices=["splunk", "elk", "syslog", "ndjson"], default="elk")
    export.add_argument("--since", type=float, help="Hours to look back")


def handle(args) -> None:
    """Handle the compliance subcommand.

    An Improver should call this from gate-cli's command dispatcher.
    """
    try:
        from gate_compliance.store import AuditStore
        from gate_compliance.report import ComplianceReporter
        from gate_compliance.alerts import run_all_checks
        from gate_compliance.siem_export import SIEMExporter
    except ImportError:
        print("gate-compliance not installed. Run: pip install gate-compliance")
        return

    db_path = getattr(args, "db", "gate_audit.db")
    store = AuditStore(db_path)
    cmd = getattr(args, "compliance_cmd", "report")

    if cmd == "report":
        reporter = ComplianceReporter(store)
        fmt = getattr(args, "format", "text")
        since_h = getattr(args, "since", None)
        since = _since_iso(since_h) if since_h else None

        if fmt == "json":
            print(reporter.json_report(since=since))
        elif fmt == "csv":
            print(reporter.csv_export(since=since))
        else:
            print(reporter.text_report(since=since))

    elif cmd == "stats":
        print(f"Total events:    {store.count()}")
        print(f"Filter calls:    {store.count(event_type='filter')}")
        print(f"Suppressions:    {store.count(event_type='suppress')}")
        print(f"Envelopes:       {store.count(event_type='envelope_issued')}")
        print(f"Tamper detected: {store.count(event_type='envelope_tampered')}")
        print(f"Crisis events:   {store.count(mode_zone='crisis')}")

    elif cmd == "alerts":
        alerts = run_all_checks(store)
        if not alerts:
            print("No alerts triggered.")
        for a in alerts:
            print(f"[{a.severity.upper()}] {a.alert_type}: {a.message}")

    elif cmd == "export":
        exporter = SIEMExporter(store)
        fmt = getattr(args, "format", "elk")
        since_h = getattr(args, "since", None)
        since = _since_iso(since_h) if since_h else None

        if fmt == "splunk":
            for line in exporter.splunk_kv(since=since):
                print(line)
        elif fmt == "syslog":
            for line in exporter.syslog_format(since=since):
                print(line)
        elif fmt == "ndjson":
            print(exporter.elk_ndjson(since=since))
        else:
            import json
            for doc in exporter.elk_format(since=since):
                print(json.dumps(doc))


def _since_iso(hours: float) -> str:
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
