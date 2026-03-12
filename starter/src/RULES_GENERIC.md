# Generic Implementation Rules (Syntax & Conventions)

These rules describe implementation conventions inferred from the current `src/` codebase, without tying them to specific demo business content.

## 1) Placeholder and variable conventions

- Use `##VARIABLE_NAME##` placeholders in templates/scripts for values injected during build/deploy.
- For optional placeholders, use `##OPTIONAL/VARIABLE_NAME##`.
- Runtime/deploy variables are exported with `TF_VAR_*` naming where applicable.

## 2) Shell scripting conventions

- Use Bash (`#!/usr/bin/env bash`) for automation scripts.
- Resolve script directory via `BASH_SOURCE[0]` before relative path operations.
- Fail fast on unmet preconditions (missing env var/input).
- Keep scripts idempotent where possible (safe to rerun on same host).
- Use system packages/services standard to Oracle Linux environment (`dnf`, `systemd`, `firewalld`).

## 3) Java/Spring conventions

- Use Spring Boot application structure with:
  - `@SpringBootApplication` entrypoint
  - `@RestController` for HTTP endpoints
  - JPA entities with `@Entity` and `@Table`
  - repository interfaces extending `JpaRepository`
- Keep entity fields mapped directly to table columns with explicit getters/setters.

## 4) UI conventions

- UI is static HTML/CSS/JS and should consume backend APIs through relative URLs.
- JavaScript should:
  - call REST endpoints asynchronously,
  - parse JSON payloads,
  - render structured output in dedicated DOM containers.
- Containerized UI should be served from NGINX document root.

## 5) Terraform conventions

- Separate concerns across files (provider, variables, network, compute, database, outputs, orchestration).
- Use locals for derived values and naming composition.
- Use outputs for values consumed by shell tooling.
- Generate environment bridge files (e.g., `target/tf_env.sh`) for post-terraform scripting.

## 6) Deployment artifact conventions

- Keep generated/runtime artifacts under `target/`.
- Keep reusable source assets under `src/` and treat them as templates when placeholders exist.
- Build and deploy steps should support both compute-style and container-style targets.