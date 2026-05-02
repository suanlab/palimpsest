<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# deploy

## Purpose
Deployment configuration for production services.

## Key Files

| File | Description |
|------|-------------|
| `palimpsest-api.service` | systemd unit for the SciGraph API server (port 8300, runs via `uv run python scripts/run_api.py`) |

## For AI Agents

### Working In This Directory
- Service runs as user `suanlab` with docker.service dependency
- API binds to `0.0.0.0:8300` in production
- Restarts on failure with 5-second delay
- Logs go to systemd journal (`journalctl -u palimpsest-api`)

### Deployment Commands
```bash
sudo systemctl enable palimpsest-api    # Enable on boot
sudo systemctl start palimpsest-api     # Start service
sudo systemctl status palimpsest-api    # Check status
sudo journalctl -u palimpsest-api -f    # Tail logs
```

## Dependencies

### Internal
- `scripts/run_api.py` — Entry point launched by the service
- `docker-compose.yml` — Neo4j container (required dependency)

<!-- MANUAL: -->
