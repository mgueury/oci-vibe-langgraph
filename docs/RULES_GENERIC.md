# RULES_GENERIC.md

## Code Style and Architecture Guidelines

### General Principles
- **Follow existing patterns** in the codebase for consistency
- **Use async/await** for all I/O operations (FastAPI, database, network)
- **Keep functions small** and single-responsibility
- **Add clear docstrings** for all public functions and classes
- **Use type hints** where possible for better maintainability

### Python Code Style
- Follow **PEP 8** with **Black** formatting
- Use **double quotes** for strings
- **f-strings** for string formatting when possible
- **4 spaces** indentation
- **Snake_case** for variables and functions, **PascalCase** for classes
- Import order: standard library → third-party → local

### FastMCP / LangGraph Patterns
- Use `@mcp.tool()` decorator for MCP tools
- Inject user context using `context.user_id` or similar
- Return structured data with `artifact` for UI rendering
- Use `langchain_mcp_adapters` for LangGraph ↔ MCP integration

### Error Handling
- Use specific exceptions instead of generic ones
- Log errors with appropriate levels
- Return user-friendly error messages

### Security
- Never hardcode credentials
- Use environment variables for configuration
- Validate all inputs
- Follow least privilege principle for tools

### Documentation
- Keep comments up-to-date
- Document complex business logic
- Include usage examples for tools

### UI / Frontend
- Use semantic HTML
- Keep JavaScript modular
- Use modern ES6+ features
- Ensure accessibility (ARIA labels, keyboard support)

### Terraform / Infrastructure
- Use consistent naming convention (`${var.prefix}-*`)
- Group related resources
- Use data sources when possible
- Tag all resources with `freeform_tags`

Last updated: 2026-02-04
