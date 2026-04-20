"""gate tools — tool registration, filtering, validation, and export."""

import json
from pathlib import Path

import click

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from gate_cli.client import GateHTTPClient, GateServerError
from gate_cli.output import render, success, error


@click.group()
def tools():
    """Tool registration, filtering, and validation."""
    pass


@tools.command(name="register")
@click.option("--file", "-f", "file_path", required=True,
              type=click.Path(exists=True),
              help="JSON or YAML file containing tool definitions")
@click.pass_context
def register(ctx, file_path):
    """Register tools from a JSON/YAML file."""
    path = Path(file_path)
    raw = path.read_text()
    if path.suffix in (".yaml", ".yml") and HAS_YAML:
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)

    tool_list = data if isinstance(data, list) else data.get("tools", [data])

    if ctx.obj["local"]:
        _register_local(tool_list)
        return

    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        result = client.register_tools(tool_list)
        success(f"Registered {result.get('registered', '?')} tools "
                f"(total: {result.get('total', '?')})")
    except GateServerError as e:
        error(f"Registration failed: {e}")


def _register_local(tool_list):
    """Register tools using gate-core directly (no server)."""
    from maelstrom_gate import Gate, Tool
    gate = Gate()
    for t in tool_list:
        gate.add_tool(Tool(
            name=t["name"],
            execution_class=t.get("execution_class", "read_only"),
            description=t.get("description", ""),
            inputs=t.get("inputs", {}),
        ))
    success(f"Registered {len(tool_list)} tools locally")


@tools.command(name="list")
@click.pass_context
def list_tools(ctx):
    """List all registered tools."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.list_tools()
        render(data, ctx.obj["output"], title="Registered Tools",
               columns=["name", "execution_class", "description"])
    except Exception as e:
        error(f"Cannot list tools: {e}")


@tools.command()
@click.option("--mode", "-m", type=float, required=True,
              help="Threat mode signal (0.0-1.0)")
@click.option("--file", "-f", "file_path", type=click.Path(exists=True),
              help="Tool file for local one-shot filter (implies --local)")
@click.pass_context
def filter(ctx, mode, file_path):
    """Filter tools at a given mode signal."""
    if file_path or ctx.obj["local"]:
        _filter_local(ctx, mode, file_path)
        return

    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.filter_tools(mode)
        click.echo(f"Mode: {data['mode']} ({data['mode_status']})")
        click.echo()
        visible = data.get("visible", [])
        suppressed = data.get("suppressed", [])
        render(visible, ctx.obj["output"], title="Visible Tools",
               columns=["name", "execution_class"])
        if suppressed:
            click.echo()
            render(suppressed, ctx.obj["output"], title="Suppressed Tools",
                   columns=["name", "execution_class"])
    except Exception as e:
        error(f"Filter failed: {e}")


def _filter_local(ctx, mode, file_path):
    """One-shot local filter: load tools from file, filter at mode."""
    if not file_path:
        error("Local filter requires --file (-f) with tool definitions")
        return
    from maelstrom_gate import Gate, Tool

    path = Path(file_path)
    raw = path.read_text()
    if path.suffix in (".yaml", ".yml") and HAS_YAML:
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)

    tool_list = data if isinstance(data, list) else data.get("tools", [data])
    gate = Gate()
    for t in tool_list:
        gate.add_tool(Tool(
            name=t["name"],
            execution_class=t.get("execution_class", "read_only"),
            description=t.get("description", ""),
            inputs=t.get("inputs", {}),
        ))

    result = gate.filter(mode)
    click.echo(f"Mode: {result.mode} ({result.mode_status}) [local]")
    click.echo()
    visible = [{"name": t.name, "execution_class": t.execution_class}
               for t in result.visible]
    suppressed = [{"name": t.name, "execution_class": t.execution_class}
                  for t in result.suppressed]
    render(visible, ctx.obj["output"], title="Visible Tools",
           columns=["name", "execution_class"])
    if suppressed:
        click.echo()
        render(suppressed, ctx.obj["output"], title="Suppressed Tools",
               columns=["name", "execution_class"])


@tools.command()
@click.argument("tool_name")
@click.option("--mode", "-m", type=float, default=0.0,
              help="Threat mode signal (0.0-1.0)")
@click.pass_context
def validate(ctx, tool_name, mode):
    """Validate whether a tool is allowed at the given mode."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.validate_tool(tool_name, mode)
        if data.get("accepted"):
            success(f"{tool_name} is ACCEPTED at mode {mode}")
        else:
            error(f"{tool_name} is REJECTED at mode {mode}: "
                  f"{data.get('reason', 'unknown')}")
        if data.get("detail"):
            click.echo(f"  Detail: {data['detail']}")
    except GateServerError as e:
        error(f"Validation error: {e}")


@tools.command()
@click.argument("name")
@click.pass_context
def remove(ctx, name):
    """Remove a registered tool by name."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        client.remove_tool(name)
        success(f"Removed tool: {name}")
    except GateServerError as e:
        error(f"Remove failed: {e}")


@tools.command(name="export")
@click.option("--mode", "-m", type=float, default=0.0,
              help="Threat mode signal for export")
@click.option("--format", "fmt", type=click.Choice(["openai"]),
              default="openai", help="Export format")
@click.pass_context
def export_tools(ctx, mode, fmt):
    """Export tools in provider-compatible format."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.export_openai(mode)
        render(data, "json", title=f"OpenAI Tools (mode={mode})")
    except Exception as e:
        error(f"Export failed: {e}")
