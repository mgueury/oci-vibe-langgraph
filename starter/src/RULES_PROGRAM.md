# Program-Specific Rules (OCI Starter Demo)

These rules define behavior specific to this program/demo (tables, endpoints, UI wiring, and infra defaults).

## 1) Demo data model rules

- The demo schema contains at least these tables:
  - `DEPT(DEPTNO PK, DNAME, LOC)`
  - `EMP(EMPNO PK, ENAME, JOB, DEPTNO FK -> DEPT.DEPTNO)`
- Database bootstrap script `src/db/oracle.sql` is the source of truth for initial schema + seed data.

## 2) REST API rules for the demo

- Backend endpoints exposed by `DemoController`:
  - `GET /dept` → JSON list of departments
  - `GET /emp` → JSON list of employees
  - `GET /info` → plain text service/host info
- API routes are consumed in UI via `/app/*` path behind NGINX proxy.

## 3) UI behavior rules for the demo

- Main page (`src/ui/ui/index.html`) must display:
  - DEPT JSON + DEPT table
  - EMP JSON + EMP table
  - INFO text
- Frontend script (`src/ui/ui/script.js`) must call:
  - `app/dept`
  - `app/emp`
  - `app/info`
- NGINX compute routing (`src/compute/nginx_app.locations`) must keep `/app/` proxied to backend port `8080`.

## 4) Build/deploy defaults for this demo

- Default generated environment in Terraform orchestration targets:
  - `TF_VAR_deploy_type="public_compute"`
  - `TF_VAR_db_type="autonomous"`
  - Java + SpringBoot + HTML UI settings as emitted in `target/tf_env.sh`.
- Build completion file (`target/done.txt`) should include API links, including demo REST routes.

## 5) Infra composition rules for this demo

- Terraform composes:
  - VCN/networking (web/app/db subnets)
  - one compute instance
  - one ATP database
  - build/deploy orchestration via `null_resource` steps
- DB init (`src/db/db_init.sh`) applies `oracle.sql`, so schema changes must be reflected there to be deployable.