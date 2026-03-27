import os
from typing import Any

import oracledb
from fastmcp import FastMCP  # Import FastMCP, the quickstart server base

mcp = FastMCP("MCP Server")  # Initialize an MCP server instance with a descriptive name

def log( s ): 
    print( s, flush=True )

@mcp.tool()  # Register a function as a callable tool for the model
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    log( "<add>")
    return a + b  # Simple arithmetic logic


@mcp.tool()
def get_dept() -> list[dict[str, Any]]:
    """Return all rows from the DEPT table."""
    log( "<get_dept>")
    user = os.getenv("TF_VAR_db_user")
    password = os.getenv("TF_VAR_db_password")
    dsn = os.getenv("DB_URL")

    if not user or not password or not dsn:
        raise ValueError("Missing DB_USER, DB_PASSWORD, or DB_URL environment variable")

    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    log( "<get_dept>: connected to db")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DEPTNO, DNAME, LOC FROM DEPT ORDER BY DEPTNO")
            rows = cursor.fetchall()
            return [
                {"deptno": deptno, "dname": dname, "loc": loc}
                for deptno, dname, loc in rows
            ]
    finally:
        connection.close()

@mcp.tool()
def get_emp() -> list[dict[str, Any]]:
    """Return all rows from the EMP table."""
    log( "<get_emp>")
    user = os.getenv("TF_VAR_db_user")
    password = os.getenv("TF_VAR_db_password")
    dsn = os.getenv("DB_URL")

    if not user or not password or not dsn:
        raise ValueError("Missing DB_USER, DB_PASSWORD, or DB_URL environment variable")

    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    log( "<get_emp>: connected to db")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT EMPNO, ENAME, JOB, MGR, DEPTNO FROM EMP ORDER BY EMPNO")
            rows = cursor.fetchall()
            return [
                {"empno": empno, "ename": ename, "job": job, "mgr": mgr, "deptno": deptno}
                for empno, ename, job, mgr, deptno in rows
            ]
    finally:
        connection.close()


# Optional HTTP probe endpoints (when supported by installed FastMCP version)
if hasattr(mcp, "custom_route"):
    @mcp.custom_route("/health", methods=["GET"])
    async def health(_request):
        return {"status": "ok"}

    @mcp.custom_route("/ready", methods=["GET"])
    async def ready(_request):
        return {"status": "ready"}

if __name__ == "__main__":
    # mcp.run(transport="stdio")  # Run the server, using standard input/output for communication
    port = int(os.getenv("PORT", "2025"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
