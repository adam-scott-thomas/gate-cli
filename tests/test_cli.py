"""Smoke tests for gate-cli — verifies command structure loads."""

from click.testing import CliRunner

from gate_cli.main import cli


runner = CliRunner()


def test_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "server" in result.output
    assert "tools" in result.output
    assert "envelope" in result.output
    assert "policy" in result.output
    assert "status" in result.output


def test_server_help():
    result = runner.invoke(cli, ["server", "--help"])
    assert result.exit_code == 0
    assert "health" in result.output
    assert "info" in result.output
    assert "history" in result.output


def test_tools_help():
    result = runner.invoke(cli, ["tools", "--help"])
    assert result.exit_code == 0
    assert "register" in result.output
    assert "filter" in result.output
    assert "validate" in result.output
    assert "remove" in result.output
    assert "export" in result.output


def test_envelope_help():
    result = runner.invoke(cli, ["envelope", "--help"])
    assert result.exit_code == 0
    assert "build" in result.output
    assert "verify" in result.output


def test_policy_help():
    result = runner.invoke(cli, ["policy", "--help"])
    assert result.exit_code == 0
    assert "validate" in result.output
    assert "inspect" in result.output
    assert "test" in result.output


def test_compliance_help():
    result = runner.invoke(cli, ["compliance", "--help"])
    assert result.exit_code == 0
    assert "report" in result.output
    assert "check" in result.output
    assert "alerts" in result.output
    assert "export" in result.output


def test_agent_help():
    result = runner.invoke(cli, ["agent", "--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "test" in result.output
    assert "info" in result.output


def test_watch_help():
    result = runner.invoke(cli, ["watch", "--help"])
    assert result.exit_code == 0
    assert "interval" in result.output


def test_agent_info():
    result = runner.invoke(cli, ["agent", "info"])
    assert result.exit_code == 0
    assert "gate-agent" in result.output


def test_server_unreachable():
    """Connection errors should produce clean error messages."""
    result = runner.invoke(cli, ["--server-url", "http://localhost:9999/api/v1",
                                  "server", "health"])
    assert result.exit_code == 0  # Click doesn't propagate, error is printed
    assert "Cannot connect" in result.output or "error" in result.output.lower()
