"""gate compliance — compliance reporting commands.

Two backends:
  1. gate-compliance (if installed) — rich reporting with AuditStore
  2. gate-server mode history (fallback) — basic aggregation

Merged from Creator 1 (argparse) and Creator 2 (Click) versions.
"""

import click

from gate_cli.client import GateHTTPClient, GateServerError
from gate_cli.output import render, success, error, warn


def _has_gate_compliance() -> bool:
    try:
        from gate_compliance.cli_hook import is_available
        return is_available()
    except ImportError:
        return False


@click.group()
def compliance():
    """Compliance reporting and evidence generation."""
    pass


@compliance.command()
@click.option("--since", type=float, default=None,
              help="Hours to look back (e.g. 24 for last day)")
@click.option("--format", "fmt", type=click.Choice(["table", "json", "csv"]),
              default=None, help="Report format (overrides -o)")
@click.pass_context
def report(ctx, since, fmt):
    """Generate a compliance report."""
    output_fmt = fmt or ctx.obj["output"]

    # Try gate-compliance first (richer data)
    if _has_gate_compliance():
        try:
            from gate_compliance.cli_hook import generate_report
            report_fmt = fmt if fmt in ("json", "csv") else "text"
            result = generate_report(format=report_fmt, since_hours=since)
            click.echo(result)
            return
        except Exception:
            warn("gate-compliance failed, falling back to server mode history")

    # Fallback: aggregate from gate-server mode history
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        hist = client.mode_history()
        entries = hist.get("entries", [])
        if not entries:
            warn("No mode history -- nothing to report")
            return

        crisis = sum(1 for e in entries if e.get("mode_status") == "crisis")
        elevated = sum(1 for e in entries if e.get("mode_status") == "elevated")
        normal = sum(1 for e in entries if e.get("mode_status") == "normal")
        modes = [e["mode"] for e in entries]
        total_suppressed = sum(e.get("suppressed_count", 0) for e in entries)

        data = {
            "total_operations": len(entries),
            "crisis_operations": crisis,
            "elevated_operations": elevated,
            "normal_operations": normal,
            "peak_mode": max(modes),
            "average_mode": round(sum(modes) / len(modes), 3),
            "total_suppressions": total_suppressed,
            "suppression_rate": round(
                sum(1 for e in entries if e.get("suppressed_count", 0) > 0)
                / len(entries), 3
            ),
        }
        render(data, output_fmt, title="Compliance Report")
    except GateServerError as e:
        error(f"Server error: {e}")
    except Exception as e:
        error(f"Cannot generate report: {e}")


@compliance.command()
@click.pass_context
def check(ctx):
    """Quick compliance health check -- flag any red flags."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        hist = client.mode_history()
        entries = hist.get("entries", [])
        if not entries:
            warn("No operational data to check")
            return

        issues = 0
        crisis = [e for e in entries if e.get("mode_status") == "crisis"]
        if crisis:
            warn(f"{len(crisis)} crisis-mode operations detected")
            issues += 1
        else:
            success("No crisis-mode operations")

        total_suppressed = sum(e.get("suppressed_count", 0) for e in entries)
        if total_suppressed > 0:
            click.echo(f"  {total_suppressed} total tool suppressions recorded")

        if issues == 0:
            success("Compliance check passed -- no red flags")
        else:
            warn(f"Compliance check found {issues} concern(s)")
    except GateServerError as e:
        error(f"Server error: {e}")
    except Exception as e:
        error(f"Compliance check failed: {e}")


@compliance.command()
@click.option("--db", default="gate_audit.db", help="Audit database path")
@click.pass_context
def alerts(ctx, db):
    """Run compliance alert checks (requires gate-compliance)."""
    if not _has_gate_compliance():
        error("gate-compliance not installed. Install with: pip install gate-compliance")
        return
    try:
        from gate_compliance.store import AuditStore
        from gate_compliance.alerts import run_all_checks
        store = AuditStore(db)
        fired = run_all_checks(store)
        if not fired:
            success("No compliance alerts triggered")
            return
        for a in fired:
            marker = {"critical": "!!!", "warning": " ! ", "info": "   "}.get(a.severity, "   ")
            click.echo(f"[{marker}] {a.severity.upper()}: {a.alert_type}")
            click.echo(f"      {a.message}")
    except Exception as e:
        error(f"Alert check failed: {e}")


@compliance.command(name="export")
@click.option("--format", "fmt", type=click.Choice(["splunk", "elk", "syslog", "ndjson"]),
              default="elk", help="SIEM export format")
@click.option("--since", type=float, default=None, help="Hours to look back")
@click.option("--db", default="gate_audit.db", help="Audit database path")
@click.pass_context
def export_cmd(ctx, fmt, since, db):
    """Export audit trail to SIEM format (requires gate-compliance)."""
    if not _has_gate_compliance():
        error("gate-compliance not installed. Install with: pip install gate-compliance")
        return
    try:
        from gate_compliance.store import AuditStore
        from gate_compliance.siem_export import SIEMExporter
        from datetime import datetime, timedelta, timezone
        import json

        store = AuditStore(db)
        exporter = SIEMExporter(store)
        since_iso = None
        if since:
            since_iso = (datetime.now(timezone.utc) - timedelta(hours=since)).isoformat()

        if fmt == "splunk":
            for line in exporter.splunk_kv(since=since_iso):
                click.echo(line)
        elif fmt == "syslog":
            for line in exporter.syslog_format(since=since_iso):
                click.echo(line)
        elif fmt == "ndjson":
            click.echo(exporter.elk_ndjson(since=since_iso))
        else:
            for doc in exporter.elk_format(since=since_iso):
                click.echo(json.dumps(doc))
    except Exception as e:
        error(f"SIEM export failed: {e}")


# Keep legacy 'snapshot' as alias for 'report'
@compliance.command(hidden=True)
@click.pass_context
def snapshot(ctx):
    """Alias for 'report' (backwards compat)."""
    ctx.invoke(report)
