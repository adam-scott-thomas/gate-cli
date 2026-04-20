"""gate agent — manage and inspect gate-agent instances.

Wires gate-cli (Layer 3) to gate-agent (Layer 3, FROZEN).
"""

import json

import click

from gate_cli.output import render, success, error, warn


def _get_agent():
    """Import and return a GateAgent instance."""
    try:
        from gate_agent.runtime import GateAgent
        from gate_agent.mode_sources import from_env
        return GateAgent(name="cli-managed", mode_source=from_env())
    except ImportError:
        return None


@click.group()
def agent():
    """Manage gate-agent instances."""
    pass


@agent.command()
@click.option("--file", "-f", "file_path", type=click.Path(exists=True),
              help="Tool definitions (JSON/YAML) for the agent")
@click.option("--mode", "-m", type=float, default=None,
              help="Mode signal override (default: reads GATE_MODE env)")
@click.pass_context
def run(ctx, file_path, mode):
    """Run a gate-agent with tools from a file."""
    try:
        from gate_agent.runtime import GateAgent
        from gate_agent.mode_sources import from_static, from_env
    except ImportError:
        error("gate-agent not installed. Run: pip install gate-agent")
        return

    source = from_static(mode) if mode is not None else from_env()
    ag = GateAgent(name="cli-agent", mode_source=source)

    if file_path:
        import json as _json
        from pathlib import Path
        p = Path(file_path)
        raw = p.read_text()
        try:
            import yaml
            data = yaml.safe_load(raw) if p.suffix in (".yaml", ".yml") else _json.loads(raw)
        except ImportError:
            data = _json.loads(raw)

        tool_list = data if isinstance(data, list) else data.get("tools", [data])
        for t in tool_list:
            ag.register_tool(
                t["name"], t.get("execution_class", "read_only"),
                lambda _t=t: f"[stub: {_t['name']}]",
                t.get("description", ""),
            )
        success(f"Registered {len(tool_list)} tools")

    available = ag.filter_available()
    click.echo(f"Mode: {available['mode']} ({available['mode_status']})")
    render(
        [{"name": n, "status": "visible"} for n in available["visible"]] +
        [{"name": n, "status": "suppressed"} for n in available["suppressed"]],
        ctx.obj["output"],
        title="Agent Tool Status",
        columns=["name", "status"],
    )


@agent.command()
@click.option("--file", "-f", "file_path", required=True,
              type=click.Path(exists=True),
              help="Tool definitions for the agent")
@click.option("--mode", "-m", type=float, required=True,
              help="Mode signal to test at")
@click.argument("tool_name")
@click.pass_context
def test(ctx, file_path, mode, tool_name):
    """Test if an agent would allow a specific tool at a given mode."""
    try:
        from gate_agent.runtime import GateAgent
        from gate_agent.mode_sources import from_static
    except ImportError:
        error("gate-agent not installed")
        return

    ag = GateAgent(name="test-agent", mode_source=from_static(mode))

    import json as _json
    from pathlib import Path
    p = Path(file_path)
    raw = p.read_text()
    try:
        import yaml
        data = yaml.safe_load(raw) if p.suffix in (".yaml", ".yml") else _json.loads(raw)
    except ImportError:
        data = _json.loads(raw)

    tool_list = data if isinstance(data, list) else data.get("tools", [data])
    for t in tool_list:
        ag.register_tool(
            t["name"], t.get("execution_class", "read_only"),
            lambda _t=t: f"[stub: {_t['name']}]",
            t.get("description", ""),
        )

    result = ag.act(tool_name)
    if result.executed:
        success(f"{tool_name} ALLOWED at mode {mode} ({result.mode_status})")
    else:
        error(f"{tool_name} BLOCKED at mode {mode}: {result.reason}")


@agent.command()
@click.pass_context
def info(ctx):
    """Show gate-agent installation info."""
    try:
        import gate_agent
        success(f"gate-agent v{gate_agent.__version__} installed")

        from gate_agent.mode_sources import from_env
        source = from_env()
        mode = source()
        click.echo(f"  GATE_MODE: {mode}")
    except ImportError:
        error("gate-agent not installed")
