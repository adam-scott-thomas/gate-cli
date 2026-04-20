"""Integration tests — run against a live gate-server.

These tests require gate-server running at localhost:8900.
Skip with: pytest -m "not integration"
"""

import json
import os
import pytest
from click.testing import CliRunner

from gate_cli.main import cli

runner = CliRunner()

# Skip all tests if server isn't reachable
pytestmark = pytest.mark.skipif(
    os.environ.get("GATE_SKIP_INTEGRATION") == "1",
    reason="GATE_SKIP_INTEGRATION=1",
)


def _invoke(*args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


class TestServerCommands:
    def test_health(self):
        result = _invoke("server", "health")
        assert result.exit_code == 0
        assert "version" in result.output

    def test_info(self):
        result = _invoke("server", "info")
        assert result.exit_code == 0
        assert "localhost:8900" in result.output


class TestToolWorkflow:
    """Register → list → filter → validate → remove."""

    def test_register_from_file(self, tmp_path):
        tools_file = tmp_path / "tools.json"
        tools_file.write_text(json.dumps({"tools": [
            {"name": "test_read", "execution_class": "read_only",
             "description": "test tool"},
            {"name": "test_danger", "execution_class": "high_impact",
             "description": "dangerous test tool"},
        ]}))
        result = _invoke("tools", "register", "-f", str(tools_file))
        assert result.exit_code == 0
        assert "Registered 2 tools" in result.output

    def test_list(self):
        result = _invoke("tools", "list")
        assert result.exit_code == 0

    def test_filter_normal(self):
        result = _invoke("tools", "filter", "--mode", "0.1")
        assert result.exit_code == 0
        assert "normal" in result.output
        assert "Visible" in result.output

    def test_filter_crisis(self):
        result = _invoke("tools", "filter", "--mode", "0.9")
        assert result.exit_code == 0
        assert "crisis" in result.output

    def test_validate_accepted(self):
        result = _invoke("tools", "validate", "test_read", "--mode", "0.9")
        assert result.exit_code == 0
        assert "ACCEPTED" in result.output

    def test_validate_rejected(self):
        result = _invoke("tools", "validate", "test_danger", "--mode", "0.9")
        assert result.exit_code == 0
        assert "REJECTED" in result.output

    def test_export_openai(self):
        result = _invoke("tools", "export", "--mode", "0.1")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


class TestEnvelopeWorkflow:
    def test_build(self):
        result = _invoke("envelope", "build", "--tool", "test_read", "--mode", "0.2")
        assert result.exit_code == 0
        assert "Envelope built" in result.output
        assert "envelope_id" in result.output

    def test_build_json(self):
        result = _invoke("-o", "json", "envelope", "build",
                         "--tool", "test_read", "--mode", "0.2")
        assert result.exit_code == 0
        env = json.loads(result.output)
        assert env["tool_name"] == "test_read"
        assert "signature" in env

    def test_round_trip_verify(self, tmp_path):
        """Build → save → verify round-trip."""
        result = _invoke("-o", "json", "envelope", "build",
                         "--tool", "test_read", "--mode", "0.2")
        env = json.loads(result.output)
        env_file = tmp_path / "envelope.json"
        env_file.write_text(json.dumps(env))
        result = _invoke("envelope", "verify", "-f", str(env_file))
        assert result.exit_code == 0
        assert "VALID" in result.output

    def test_tamper_detection(self, tmp_path):
        """Build → tamper → verify detects forgery."""
        result = _invoke("-o", "json", "envelope", "build",
                         "--tool", "test_read", "--mode", "0.2")
        env = json.loads(result.output)
        env["budget_seconds"] = 999  # tamper
        env_file = tmp_path / "tampered.json"
        env_file.write_text(json.dumps(env))
        result = _invoke("envelope", "verify", "-f", str(env_file))
        assert result.exit_code == 0
        assert "INVALID" in result.output


class TestYAMLSupport:
    def test_register_yaml(self, tmp_path):
        yaml_content = """tools:
  - name: yaml_test
    execution_class: read_only
    description: registered from YAML
"""
        yaml_file = tmp_path / "tools.yaml"
        yaml_file.write_text(yaml_content)
        result = _invoke("tools", "register", "-f", str(yaml_file))
        assert result.exit_code == 0
        assert "Registered 1 tools" in result.output

    def test_local_filter_yaml(self, tmp_path):
        yaml_content = """tools:
  - name: yaml_safe
    execution_class: read_only
  - name: yaml_danger
    execution_class: high_impact
"""
        yaml_file = tmp_path / "tools.yaml"
        yaml_file.write_text(yaml_content)
        result = _invoke("--local", "tools", "filter",
                         "--mode", "0.9", "-f", str(yaml_file))
        assert result.exit_code == 0
        assert "yaml_safe" in result.output
        assert "Suppressed" in result.output


class TestLocalMode:
    def test_local_filter(self, tmp_path):
        tools_file = tmp_path / "tools.json"
        tools_file.write_text(json.dumps({"tools": [
            {"name": "local_safe", "execution_class": "read_only"},
            {"name": "local_risky", "execution_class": "high_impact"},
        ]}))
        result = _invoke("--local", "tools", "filter",
                         "--mode", "0.9", "-f", str(tools_file))
        assert result.exit_code == 0
        assert "local" in result.output
        assert "local_safe" in result.output


class TestAgentIntegration:
    """Test gate agent commands — requires gate-agent installed."""

    def test_agent_info(self):
        result = _invoke("agent", "info")
        assert result.exit_code == 0
        assert "gate-agent" in result.output

    def test_agent_run_with_file(self, tmp_path):
        tools_file = tmp_path / "tools.json"
        tools_file.write_text(json.dumps({"tools": [
            {"name": "safe", "execution_class": "read_only"},
            {"name": "risky", "execution_class": "high_impact"},
        ]}))
        result = _invoke("agent", "run", "-f", str(tools_file), "--mode", "0.9")
        assert result.exit_code == 0
        assert "safe" in result.output
        assert "suppressed" in result.output

    def test_agent_test_allowed(self, tmp_path):
        tools_file = tmp_path / "tools.json"
        tools_file.write_text(json.dumps({"tools": [
            {"name": "safe_tool", "execution_class": "read_only"},
        ]}))
        result = _invoke("agent", "test", "-f", str(tools_file),
                         "--mode", "0.9", "safe_tool")
        assert result.exit_code == 0
        assert "ALLOWED" in result.output

    def test_agent_test_blocked(self, tmp_path):
        tools_file = tmp_path / "tools.json"
        tools_file.write_text(json.dumps({"tools": [
            {"name": "nuke", "execution_class": "high_impact"},
        ]}))
        result = _invoke("agent", "test", "-f", str(tools_file),
                         "--mode", "0.9", "nuke")
        assert result.exit_code == 0
        assert "BLOCKED" in result.output


class TestComplianceCommands:
    def test_compliance_report(self):
        result = _invoke("compliance", "report")
        assert result.exit_code == 0

    def test_compliance_check(self):
        result = _invoke("compliance", "check")
        assert result.exit_code == 0


class TestErrorHandling:
    def test_unreachable_server_health(self):
        result = _invoke("--server-url", "http://localhost:19999/api/v1",
                         "server", "health")
        assert result.exit_code == 0
        assert "Cannot connect" in result.output

    def test_unreachable_server_status(self):
        result = _invoke("--server-url", "http://localhost:19999/api/v1",
                         "status")
        assert result.exit_code == 0
        assert "Cannot connect" in result.output or "unreachable" in result.output.lower()


class TestStatus:
    def test_status(self):
        result = _invoke("status")
        assert result.exit_code == 0
        assert "Server online" in result.output

    def test_history(self):
        result = _invoke("server", "history")
        assert result.exit_code == 0
