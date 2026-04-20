"""gate policy — policy validation and inspection (delegates to gate-policy)."""

import json
from pathlib import Path

import click

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from gate_cli.output import render, success, error, warn


@click.group()
def policy():
    """Policy validation, inspection, and testing."""
    pass


@policy.command()
@click.option("--file", "-f", "file_path", required=True,
              type=click.Path(exists=True),
              help="Policy YAML/JSON file to validate")
@click.pass_context
def validate(ctx, file_path):
    """Validate a policy file against the gate-policy schema."""
    path = Path(file_path)
    raw = path.read_text()
    try:
        if path.suffix in (".yaml", ".yml") and HAS_YAML:
            data = yaml.safe_load(raw)
        else:
            data = json.loads(raw)
    except Exception as e:
        error(f"Cannot parse {file_path}: {e}")
        return

    try:
        from gate_policy import load_policy
        pol = load_policy(data)
        success(f"Policy is valid: {len(pol.rules)} rules loaded")
        render(
            [{"name": r.name, "action": r.action,
              "conditions": len(r.conditions)}
             for r in pol.rules],
            ctx.obj["output"],
            title="Policy Rules",
            columns=["name", "action", "conditions"],
        )
    except ImportError:
        warn("gate-policy not installed — cannot validate policy structure")
        warn("Install with: pip install -e ../gate-policy")
        click.echo(f"  Parsed {file_path}: {len(data)} top-level keys")
    except Exception as e:
        error(f"Policy validation failed: {e}")


@policy.command()
@click.option("--file", "-f", "file_path", required=True,
              type=click.Path(exists=True),
              help="Policy file to inspect")
@click.pass_context
def inspect(ctx, file_path):
    """Show policy rules and conditions in human-readable form."""
    path = Path(file_path)
    raw = path.read_text()
    try:
        if path.suffix in (".yaml", ".yml") and HAS_YAML:
            data = yaml.safe_load(raw)
        else:
            data = json.loads(raw)
    except Exception as e:
        error(f"Cannot parse {file_path}: {e}")
        return

    render(data, ctx.obj["output"], title=f"Policy: {path.name}")


@policy.command()
@click.option("--file", "-f", "file_path", required=True,
              type=click.Path(exists=True),
              help="Policy file to test against")
@click.option("--tool", "-t", "tool_name", required=True,
              help="Tool name to test")
@click.option("--mode", "-m", type=float, default=0.0)
@click.option("--role", "-r", default="default",
              help="Role to simulate")
@click.pass_context
def test(ctx, file_path, tool_name, mode, role):
    """Test a policy against a specific tool proposal."""
    try:
        from gate_policy import PolicyEngine, load_policy_file
    except ImportError:
        error("gate-policy not installed — cannot run policy tests")
        return

    try:
        pol = load_policy_file(file_path)
        engine = PolicyEngine(pol)
        result = engine.evaluate(tool_name=tool_name, mode=mode, role=role)
        if result.get("allowed"):
            success(f"{tool_name} ALLOWED by policy at mode={mode} role={role}")
        else:
            error(f"{tool_name} DENIED by policy: {result.get('reason', '?')}")
    except Exception as e:
        error(f"Policy test failed: {e}")
