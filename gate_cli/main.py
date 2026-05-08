"""Main CLI entrypoint — command group routing."""

import click

from gate_cli import __version__
from gate_cli.commands.server import server
from gate_cli.commands.tools import tools
from gate_cli.commands.envelope import envelope
from gate_cli.commands.policy import policy
from gate_cli.commands.status import status
from gate_cli.commands.compliance_click import compliance
from gate_cli.commands.watch import watch
from gate_cli.commands.agent import agent


@click.group()
@click.version_option(__version__, prog_name="gate")
@click.option("--server-url", envvar="GATE_SERVER_URL",
              default="http://localhost:8900/api/v1",
              help="Gate server base URL (env: GATE_SERVER_URL)")
@click.option("--local", is_flag=True, default=False,
              help="Run gate-core locally instead of talking to a server")
@click.option("--output", "-o", type=click.Choice(["table", "json", "yaml"]),
              default="table", help="Output format")
@click.pass_context
def cli(ctx, server_url, local, output):
    """Gatekeeper CLI — runtime governance for AI tool access."""
    ctx.ensure_object(dict)
    ctx.obj["server_url"] = server_url
    ctx.obj["local"] = local
    ctx.obj["output"] = output


cli.add_command(server)
cli.add_command(tools)
cli.add_command(envelope)
cli.add_command(policy)
cli.add_command(status)
cli.add_command(compliance)
cli.add_command(watch)
cli.add_command(agent)


if __name__ == "__main__":
    cli()
