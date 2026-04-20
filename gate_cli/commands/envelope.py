"""gate envelope — authorization envelope operations."""

import json

import click

from gate_cli.client import GateHTTPClient, GateServerError
from gate_cli.output import render, success, error


@click.group()
def envelope():
    """Authorization envelope build and verify."""
    pass


@envelope.command()
@click.option("--tool", "-t", "tool_name", required=True,
              help="Tool name to build envelope for")
@click.option("--mode", "-m", type=float, default=0.0,
              help="Threat mode signal (0.0-1.0)")
@click.option("--context-id", default="cli-session",
              help="Context identifier for the envelope")
@click.option("--human-approved", is_flag=True, default=False,
              help="Mark as human-approved")
@click.pass_context
def build(ctx, tool_name, mode, context_id, human_approved):
    """Build an authorization envelope for a tool."""
    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.build_envelope(
            tool_name=tool_name,
            mode=mode,
            context_id=context_id,
            human_approved=human_approved,
        )
        fmt = ctx.obj["output"]
        if fmt != "json":
            success(f"Envelope built for {tool_name}")
        render(data, fmt, title="Authorization Envelope")
    except GateServerError as e:
        error(f"Build failed: {e}")


@envelope.command()
@click.option("--file", "-f", "file_path", type=click.Path(exists=True),
              help="JSON file containing the envelope to verify")
@click.option("--envelope-json", "-e", "envelope_str",
              help="Envelope as inline JSON string")
@click.pass_context
def verify(ctx, file_path, envelope_str):
    """Verify an authorization envelope's signature."""
    if file_path:
        with open(file_path) as f:
            env_data = json.load(f)
    elif envelope_str:
        env_data = json.loads(envelope_str)
    else:
        error("Provide --file or --envelope-json")
        return

    client = GateHTTPClient(ctx.obj["server_url"])
    try:
        data = client.verify_envelope(env_data)
        if data.get("valid"):
            success("Envelope signature is VALID")
        else:
            error("Envelope signature is INVALID — possible tampering")
    except GateServerError as e:
        error(f"Verify failed: {e}")
