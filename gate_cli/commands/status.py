"""gate status — ecosystem-wide status overview."""

import click

from gate_cli.client import GateHTTPClient, GateServerError
from gate_cli.output import render, success, error, warn


@click.command()
@click.pass_context
def status(ctx):
    """Show gate ecosystem status: server health, tool count, mode state."""
    url = ctx.obj["server_url"]
    client = GateHTTPClient(url)

    click.echo(f"Gate Server: {url}")
    click.echo()

    # Health check
    try:
        health = client.health()
        success(f"Server online — v{health.get('version', '?')}, "
                f"{health.get('tool_count', 0)} tools registered")
    except Exception as e:
        error(f"Server unreachable: {e}")
        return

    # Tool summary
    try:
        tools = client.list_tools()
        if tools:
            by_class = {}
            for t in tools:
                cls = t.get("execution_class", "unknown")
                by_class[cls] = by_class.get(cls, 0) + 1
            click.echo()
            render(
                [{"class": k, "count": v} for k, v in sorted(by_class.items())],
                ctx.obj["output"],
                title="Tools by Execution Class",
                columns=["class", "count"],
            )
    except Exception:
        warn("Could not fetch tool list")

    # Mode history summary
    try:
        hist = client.mode_history()
        entries = hist.get("entries", [])
        if entries:
            modes = [e["mode"] for e in entries]
            latest = entries[-1]
            click.echo()
            click.echo(f"Mode History: {len(entries)} entries")
            click.echo(f"  Latest: {latest['mode']} ({latest['mode_zone']})")
            click.echo(f"  Range: {min(modes):.2f} — {max(modes):.2f}")
            click.echo(f"  Average: {sum(modes)/len(modes):.2f}")
    except Exception:
        pass
