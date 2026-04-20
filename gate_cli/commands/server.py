"""gate server — server health and info commands."""

import click

from gate_cli.client import GateHTTPClient, GateServerError
from gate_cli.output import render, success, error


@click.group()
def server():
    """Gate server health and operations."""
    pass


@server.command()
@click.pass_context
def health(ctx):
    """Check gate-server health."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.health()
        render(data, ctx.obj["output"], title="Server Health")
    except GateServerError as e:
        error(f"Server error: {e}")
    except Exception as e:
        error(f"Cannot reach server: {e}")


@server.command()
@click.pass_context
def info(ctx):
    """Show server info: version, tool count, URL."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.health()
        data["server_url"] = ctx.obj["server_url"]
        render(data, ctx.obj["output"], title="Server Info")
    except Exception as e:
        error(f"Cannot reach server: {e}")


@server.command()
@click.pass_context
def history(ctx):
    """Show mode signal history (last 100 filter operations)."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.mode_history()
        entries = data.get("entries", [])
        if not entries:
            click.echo("No mode history yet.")
            return
        render(entries, ctx.obj["output"], title="Mode History",
               columns=["timestamp", "mode", "mode_zone",
                         "visible_count", "suppressed_count"])
    except Exception as e:
        error(f"Cannot fetch history: {e}")
