# gate-cli Integration Map

## What gate-cli connects to

```
gate-cli (Layer 3)
    |
    ├── gate-server (Layer 1) ← HTTP client, all endpoints
    |       └── gate-core (Layer 0) ← runs server-side
    |
    ├── gate-core (Layer 0) ← local mode, runs in-process
    |
    ├── gate-policy (Layer 2) ← policy validate/inspect/test commands
    |
    └── gate-compliance (Layer 2) ← future: compliance report generation
```

## Connection Details

### gate-server (primary)
- **Protocol:** HTTP/JSON
- **Default URL:** `http://localhost:8900/api/v1`
- **Config:** `--server-url` flag or `GATE_SERVER_URL` env var
- **Endpoints used:**
  - `GET /health` — server health, info
  - `POST /tools/register` — register tools from file
  - `GET /tools` — list registered tools
  - `POST /tools/filter` — filter at mode signal
  - `POST /tools/validate` — validate tool proposals
  - `DELETE /tools/{name}` — remove tools
  - `POST /tools/openai` — OpenAI-compatible export
  - `POST /envelope/build` — build authorization envelope
  - `POST /envelope/verify` — verify envelope signature
  - `GET /mode/history` — mode signal history

### gate-core (local mode)
- **Flag:** `--local`
- **Import:** `from maelstrom_gate import Gate, Tool`
- **Used for:** One-shot register + filter without a running server
- **Limitation:** No envelope operations in local mode (needs signing key config)

### gate-policy (optional)
- **Import:** `from gate_policy import PolicyEngine, load_policy_file`
- **Commands:** `gate policy validate`, `gate policy inspect`, `gate policy test`
- **Graceful degradation:** If gate-policy not installed, commands warn and show raw file content

## Workflow Examples

### Quick filter check (no server needed)
```bash
gate --local tools filter --mode 0.8 -f tools.yaml
```

### Full server workflow
```bash
gate tools register -f tools.yaml
gate tools filter --mode 0.5
gate envelope build --tool read_logs --mode 0.3
gate -o json envelope build --tool read_logs --mode 0.3 > envelope.json
gate envelope verify -f envelope.json
gate status
```

### Policy testing
```bash
gate policy validate -f policy.yaml
gate policy test -f policy.yaml --tool deploy_production --mode 0.7
```

## Integration Gaps (for Improvers)

1. **gate-server-go support** — The HTTP client assumes `/api/v1` prefix. gate-server-go uses `/v1`. Add a `--backend go` flag that adjusts the prefix.
2. **Envelope verify in local mode** — Needs `GATE_SIGNING_KEY` env var support for local envelope operations.
3. **Compliance commands** — `gate compliance report` should pull from gate-compliance when it's ready.
4. **Watch mode** — `gate tools filter --mode 0.5 --watch` to continuously poll and show changes.
5. **Shell completion** — Click supports bash/zsh/fish completion generation.
