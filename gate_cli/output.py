"""Output formatting — table, JSON, YAML rendering via Rich."""
from __future__ import annotations

import json
from typing import Any

import click

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from rich.console import Console
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


console = Console() if HAS_RICH else None


def render(data: Any, fmt: str = "table", title: str = "",
           columns: list[str] | None = None):
    """Render data in the requested format."""
    if fmt == "json":
        click.echo(json.dumps(data, indent=2, default=str))
    elif fmt == "yaml":
        if HAS_YAML:
            click.echo(yaml.dump(data, default_flow_style=False))
        else:
            click.echo(json.dumps(data, indent=2, default=str))
    else:
        _render_table(data, title, columns)


def _render_table(data: Any, title: str, columns: list[str] | None):
    """Render data as a Rich table, falling back to plain text."""
    if isinstance(data, dict) and not columns:
        # Key-value display
        if HAS_RICH:
            table = Table(title=title or None)
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            for k, v in data.items():
                table.add_row(str(k), str(v))
            console.print(table)
        else:
            if title:
                click.echo(f"--- {title} ---")
            for k, v in data.items():
                click.echo(f"  {k}: {v}")
    elif isinstance(data, list):
        # List of dicts → tabular display
        if not data:
            click.echo("(empty)")
            return
        cols = columns or list(data[0].keys()) if isinstance(data[0], dict) else ["value"]
        if HAS_RICH:
            table = Table(title=title or None)
            for c in cols:
                table.add_column(c, style="cyan")
            for row in data:
                if isinstance(row, dict):
                    table.add_row(*[str(row.get(c, "")) for c in cols])
                else:
                    table.add_row(str(row))
            console.print(table)
        else:
            if title:
                click.echo(f"--- {title} ---")
            for row in data:
                click.echo(f"  {row}")
    else:
        click.echo(str(data))


def success(msg: str):
    if HAS_RICH:
        console.print(f"[green]OK[/green] {msg}")
    else:
        click.echo(f"OK: {msg}")


def error(msg: str):
    if HAS_RICH:
        console.print(f"[red]ERR[/red] {msg}")
    else:
        click.echo(f"ERROR: {msg}", err=True)


def warn(msg: str):
    if HAS_RICH:
        console.print(f"[yellow]WARN[/yellow] {msg}")
    else:
        click.echo(f"WARN: {msg}")
