"""gate watch — continuous monitoring of gate state.

Polls gate-server at intervals and shows live tool suppression state.
Useful for operators monitoring a live system.

NOT WIRED YET — An Improver should:
  1. Implement the polling loop with configurable interval
  2. Add Rich Live display for real-time table updates
  3. Add alerting thresholds (e.g., notify when crisis mode detected)
  4. Add --webhook flag for external notification integration

Seeded by Creator 2 (gate-cli), Loop 5.
"""

import time

import click

from gate_cli.client import GateHTTPClient
from gate_cli.output import render, success, error, warn


@click.command()
@click.option("--interval", "-i", type=int, default=5,
              help="Poll interval in seconds")
@click.option("--mode", "-m", type=float, default=None,
              help="Fixed mode signal to filter at (omit to show last known)")
@click.pass_context
def watch(ctx, interval, mode):
    """Continuously monitor gate server state.

    Polls the server and shows tool visibility changes in real time.
    Press Ctrl+C to stop.
    """
    client = GateHTTPClient(ctx.obj["server_url"])
    click.echo(f"Watching {ctx.obj['server_url']} every {interval}s...")
    click.echo("Press Ctrl+C to stop.")
    click.echo()

    last_visible = None
    try:
        while True:
            try:
                if mode is not None:
                    data = client.filter_tools(mode)
                    visible = {t["name"] for t in data.get("visible", [])}
                    status = data.get("mode_status", "?")
                    click.echo(f"[{time.strftime('%H:%M:%S')}] "
                               f"mode={mode} ({status}) "
                               f"visible={len(visible)} "
                               f"suppressed={len(data.get('suppressed', []))}")
                    if last_visible is not None and visible != last_visible:
                        added = visible - last_visible
                        removed = last_visible - visible
                        if added:
                            success(f"  + {', '.join(sorted(added))}")
                        if removed:
                            warn(f"  - {', '.join(sorted(removed))}")
                    last_visible = visible
                else:
                    health = client.health()
                    click.echo(f"[{time.strftime('%H:%M:%S')}] "
                               f"tools={health.get('tool_count', '?')} "
                               f"status=ok")
            except Exception as e:
                error(f"[{time.strftime('%H:%M:%S')}] {e}")
            time.sleep(interval)
    except KeyboardInterrupt:
        click.echo("\nStopped.")
