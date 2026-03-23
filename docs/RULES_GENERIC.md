# Generic Implementation Rules (Syntax & Conventions)

These rules describe implementation conventions inferred from the current `src/` codebase, without hard-coding business logic.

## Shell scripting conventions

- Use Bash for automation (`#!/usr/bin/env bash` or `#!/bin/bash`).
- Resolve script location with `BASH_SOURCE[0]` and `cd` to script directory before relative operations.
- Source environment bridges (`env.sh`, `compute/tf_env.sh`) before running dependent commands.
- Keep scripts rerunnable and explicit (`install.sh`, `start.sh`, `build_*.sh`, `db_init.sh`).

## Python service conventions

- Python components are dependency-driven by local `requirements.txt` files.
- LangGraph agent code lives under `src/app/src_langgraph/agent/`.
- MCP tools live in `src/app/src_mcp_server/mcp_server.py` and are registered with `@mcp.tool()`.
- Configuration is read from environment variables (for example `MCP_SERVER_URL`, DB credentials, OCI settings).

## UI conventions

- UI is static web content in `src/ui/ui/` (HTML/CSS/JS + assets).
- Front-end JavaScript uses `fetch` and relative URLs for backend integration.
- Keep chat behavior in `chat.js` and markup in `chat.html`.

## Container/Kubernetes conventions

- Dockerfiles are separated by component (`Dockerfile_langgraph`, `Dockerfile_mcp_server`, UI `Dockerfile`).
- Kubernetes manifests are split by service (`k8s_langgraph.yaml`, `k8s_mcp_server.yaml`, `ui.yaml`).

## Reverse proxy conventions

- NGINX path routing for compute deployment is defined in `src/compute/nginx_app.locations`.
- Keep path contracts stable (for example `/langgraph/server/` forwarding to local service port).

## Terraform conventions

- Terraform files are modularized by concern (`provider.tf`, `network.tf`, `compute.tf`, `atp.tf`, `output.tf`, etc.).
- Use Terraform outputs/environment export flow to feed runtime shell and app setup.