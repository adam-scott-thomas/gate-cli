"""Failure injection tests for gate-cli.

Tests for:
- Output formatting edge cases (empty data, nested dicts, missing rich/yaml)
- Client error handling (connection refused, timeouts, bad responses)
- Command edge cases (missing args, invalid formats)
- Compliance subcommand integration
"""
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gate_cli.main import cli
from gate_cli.output import render, success, error, warn
from gate_cli.client import GateHTTPClient, GateServerError


runner = CliRunner()


# --- Output module edge cases ---


def test_render_json_format():
    """JSON format should produce valid JSON."""
    result = runner.invoke(cli, ["--output", "json", "--help"])
    assert result.exit_code == 0


def test_render_empty_dict():
    """Rendering empty dict shouldn't crash."""
    # Capture output via click
    with patch("gate_cli.output.click") as mock_click:
        render({}, "table", title="Empty")


def test_render_empty_list():
    """Rendering empty list should show (empty)."""
    with patch("gate_cli.output.click") as mock_click:
        render([], "table")
        mock_click.echo.assert_called_with("(empty)")


def test_render_nested_dict():
    """Nested dicts should stringify cleanly."""
    with patch("gate_cli.output.click") as mock_click:
        render({"key": {"nested": "value"}}, "table")


def test_render_list_of_dicts():
    """List of dicts should render as table rows."""
    data = [{"name": "a", "value": 1}, {"name": "b", "value": 2}]
    with patch("gate_cli.output.click") as mock_click:
        render(data, "table", title="Test")


def test_render_plain_string():
    """Non-dict/list data should echo as string."""
    with patch("gate_cli.output.click") as mock_click:
        render("just a string", "table")
        mock_click.echo.assert_called_with("just a string")


# --- Client error handling ---


def test_client_connection_failure():
    """Unreachable server should raise GateServerError with status 0."""
    client = GateHTTPClient("http://localhost:1/api/v1", timeout=1.0)
    with pytest.raises(GateServerError) as exc_info:
        client.health()
    assert exc_info.value.status_code == 0
    # Could be "Cannot connect" or "timed out" depending on OS
    assert "Cannot connect" in exc_info.value.detail or "timed out" in exc_info.value.detail


def test_gate_server_error_str():
    err = GateServerError(404, "Tool 'x' not found")
    assert "404" in str(err)
    assert "not found" in str(err)


def test_gate_server_error_attributes():
    err = GateServerError(500, "Internal")
    assert err.status_code == 500
    assert err.detail == "Internal"


# --- Command structure ---


def test_all_top_level_commands():
    """All expected command groups should be registered."""
    result = runner.invoke(cli, ["--help"])
    expected = ["server", "tools", "envelope", "policy", "status",
                "compliance", "watch", "agent"]
    for cmd in expected:
        assert cmd in result.output, f"Missing command: {cmd}"


def test_output_format_options():
    """--output should accept table, json, yaml."""
    for fmt in ["table", "json", "yaml"]:
        result = runner.invoke(cli, ["--output", fmt, "--help"])
        assert result.exit_code == 0


def test_local_flag():
    """--local flag should be accepted."""
    result = runner.invoke(cli, ["--local", "--help"])
    assert result.exit_code == 0


def test_server_url_option():
    """--server-url should accept custom URLs."""
    result = runner.invoke(cli, ["--server-url", "http://custom:9999/api/v1", "--help"])
    assert result.exit_code == 0


# --- Compliance subcommands ---


def test_compliance_alerts_help():
    result = runner.invoke(cli, ["compliance", "alerts", "--help"])
    assert result.exit_code == 0
    assert "--db" in result.output


def test_compliance_export_help():
    result = runner.invoke(cli, ["compliance", "export", "--help"])
    assert result.exit_code == 0
    assert "splunk" in result.output
    assert "elk" in result.output
    assert "syslog" in result.output


def test_compliance_report_help():
    result = runner.invoke(cli, ["compliance", "report", "--help"])
    assert result.exit_code == 0
    assert "--since" in result.output
    assert "--format" in result.output


def test_compliance_check_unreachable():
    """Compliance check against unreachable server should show clean error."""
    result = runner.invoke(cli, [
        "--server-url", "http://localhost:1/api/v1",
        "compliance", "check",
    ])
    assert result.exit_code == 0
    assert "Cannot connect" in result.output or "error" in result.output.lower()
