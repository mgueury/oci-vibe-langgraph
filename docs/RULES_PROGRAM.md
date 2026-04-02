# RULES_PROGRAM.md

## Program-Specific Rules for OCI Vibe LangGraph Demo

### Business Domain
This project demonstrates **"Vibe Coding"** using OCI AI Agent API keys with:
- Sales agenda management
- Customer relationship tracking
- Oracle Database integration (DEPT/EMP tables)
- Voice input capabilities
- Multi-agent backend (LangGraph + Responses API)

### Database Schema
**Tables**:
- `DEPT` (DEPTNO, DNAME, LOC)
- `EMP` (EMPNO, ENAME, JOB, MGR, DEPTNO)

**Sample Data**:
- Departments: ACCOUNTING (10), RESEARCH (20), SALES (30), OPERATIONS (40)
- Classic Scott/Tiger EMP hierarchy

### MCP Tools (mcp_server.py)
**Sales Tools**:
- `get_agenda(user_id)`: Get user's meeting schedule
- `get_customers()`: List all customers
- `add_meeting(customer, topic, date, user_id)`: Schedule a meeting
- `record_outcome(meeting_id, outcome, user_id)`: Record meeting results

**Database Tools**:
- `get_dept()`: Return all departments
- `get_emp()`: Return all employees with department join
- `get_emp_by_dept(deptno)`: Filter employees by department

**Tool Implementation Rules**:
- All tools must accept `context` parameter for user context injection
- Return data in `{"response": "...", "result": [...]}` format for UI rendering
- Use `oracledb` async connection from environment variables
- Log all operations for debugging

### LangGraph Agent (agent.py)
- Uses `openai.gpt-oss-120b` model via `ChatOCIGenAI`
- Connects to MCP server via `MultiServerMCPClient`
- Uses `langgraph-cli` with `langgraph.json` configuration
- Authentication via `auth.py` (OAuth caching with `aiocache`)

### Responses API (responses.py)
- Alternative backend using OCI's Responses API
- Same MCP tools available
- Different endpoint (`/responses`)

### UI Behavior (chat.js)
- Supports multiple backends: LangGraph, Responses, OpenID variants
- Voice input using Web Speech API
- Markdown + Mermaid diagram rendering
- Table rendering for structured tool results
- User context switching (employee/customer)
- CSRF protection for OpenID mode

### Configuration
**Required terraform.tfvars**:
- `prefix`, `db_password`, `license_model`
- `compartment_ocid`
- `project_ocid`, `genai_api_key` (for Responses API)

**Environment Variables**:
- Database connection details passed via `tf_env.sh`
- OCI GenAI credentials
- MCP server port: 2025 (default)

### Demo Flow
1. User speaks or types request
2. Agent decides which MCP tool to call
3. Tool executes (DB query or business logic)
4. Results rendered in chat with tables/diagrams
5. Voice input → transcription → agent processing

### Extensibility Rules
- Add new tools to `mcp_server.py` using `@mcp.tool()`
- Update `langgraph.json` if changing agent graph
- Keep UI rendering logic generic in `renderMessage()`
- Update `helper/demo.txt` when adding new demo features

**Last updated**: 2026-02-04
**Version**: 1.0 (Vibe Coding Demo)
