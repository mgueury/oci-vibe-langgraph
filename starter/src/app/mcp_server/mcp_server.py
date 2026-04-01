import os
from typing import Any, Optional

import oracledb
from fastmcp import FastMCP  # Import FastMCP, the quickstart server base

mcp = FastMCP("MCP Server")  # Initialize an MCP server instance with a descriptive name

def log( s ): 
    print( s, flush=True )


WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
CURRENT_DAY = "Wednesday"
CURRENT_TIME = "08:00"
HOURS_BY_DAY: dict[str, list[str]] = {
    day: [f"{h:02d}:00" for h in range(9, 18)] for day in WEEK_DAYS
}

# Sales context: companies buying IT computer products/services.
CUSTOMERS: list[dict[str, Any]] = [
    {"id": "c1", "name": "Emma Dubois", "company": "NovaTech Systems", "location": "Brussels", "score": 6, "interest": "AI workstation refresh"},
    {"id": "c2", "name": "Lucas Martin", "company": "HelioSoft", "location": "Antwerp", "score": 8, "interest": "Secure laptop fleet"},
    {"id": "c3", "name": "Sofia Lambert", "company": "BluePeak Consulting", "location": "Ghent", "score": 4, "interest": "VDI and thin clients"},
    {"id": "c4", "name": "Noah Petit", "company": "Orbit Retail", "location": "Liège", "score": 7, "interest": "POS hardware modernization"},
    {"id": "c5", "name": "Lina Moreau", "company": "Vertex Manufacturing", "location": "Charleroi", "score": 5, "interest": "Edge compute boxes"},
    {"id": "c6", "name": "Jules Leroy", "company": "Aster Finance", "location": "Namur", "score": 9, "interest": "High-availability servers"},
    {"id": "c7", "name": "Mila Rousseau", "company": "GreenGrid Energy", "location": "Leuven", "score": 3, "interest": "Rugged field laptops"},
    {"id": "c8", "name": "Hugo Fontaine", "company": "Cobalt Health", "location": "Mons", "score": 6, "interest": "Medical workstation lifecycle"},
]

MEETING_TOPICS = [
    "Discovery workshop",
    "Infrastructure assessment",
    "Device refresh proposal",
    "Security and compliance review",
    "Budget alignment",
    "Pilot rollout planning",
    "Technical Q&A",
    "Contract negotiation",
]

AGENDA: list[dict[str, Any]] = []
LAST_RECORDED_MEETING_BY_CUSTOMER: dict[str, str] = {}


def _customer_index(customer_id: str) -> Optional[int]:
    for idx, c in enumerate(CUSTOMERS):
        if c["id"] == customer_id:
            return idx
    return None


def _customer_from_name(customer_name: str) -> Optional[dict[str, Any]]:
    needle = customer_name.strip().lower()
    for c in CUSTOMERS:
        if c["name"].lower() == needle:
            return c
    return None


def _meeting_sort_key(m: dict[str, Any]) -> tuple[int, str]:
    return (WEEK_DAYS.index(m["day"]), m["time"])


def _free_slots() -> list[dict[str, str]]:
    used = {(m["day"], m["time"]) for m in AGENDA}
    slots: list[dict[str, str]] = []
    for day in WEEK_DAYS:
        for hour in HOURS_BY_DAY[day]:
            if (day, hour) not in used:
                slots.append({"day": day, "time": hour})
    return slots


def _build_agenda() -> None:
    if AGENDA:
        return

    customer_cursor = 0
    meeting_cursor = 0
    for day in WEEK_DAYS:
        for hour in HOURS_BY_DAY[day]:
            # Keep 6-8 meetings per day; leave remaining slots free.
            hour_num = int(hour[:2])
            if hour_num in {12, 17}:
                continue
            customer = CUSTOMERS[customer_cursor % len(CUSTOMERS)]
            topic = MEETING_TOPICS[meeting_cursor % len(MEETING_TOPICS)]
            AGENDA.append(
                {
                    "id": f"m{meeting_cursor + 1}",
                    "day": day,
                    "time": hour,
                    "meeting_name": f"{topic} with {customer['company']}",
                    "meeting_goal": f"Advance {customer['interest']} project and align next sales step.",
                    "customer_id": customer["id"],
                    "customer_name": customer["name"],
                    "company": customer["company"],
                    "status": "planned",
                    "previous_notes": "No previous meeting recorded yet.",
                    "recorded_details": None,
                }
            )
            customer_cursor += 1
            meeting_cursor += 1


_build_agenda()

@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict[str, str]:
    """Email sender tool"""
    log("<send_email>")
    log(f"<send_email>: to={to}, subject={subject}")

    return {
        "status": "sent",
        "message": f"Email sent to {to} with subject '{subject}'",
    }


@mcp.tool()
def get_today_agenda() -> dict[str, Any]:
    """Return today's planned agenda (demo current day is fixed to Wednesday)."""
    log("<get_today_agenda>")
    today_meetings = [
        m for m in sorted(AGENDA, key=_meeting_sort_key)
        if m["day"] == CURRENT_DAY and m["status"] == "planned"
    ]
    return {
        "currentDay": CURRENT_DAY,
        "currentTime": CURRENT_TIME,
        "planned_meetings": [
            {
                "meeting_id": m["id"],
                "time": m["time"],
                "meeting_name": m["meeting_name"],
                "customer_name": m["customer_name"],
                "company": m["company"],
                "status": m["status"],
            }
            for m in today_meetings
        ],
    }


@mcp.tool()
def get_week_agenda() -> list[list[Any]]:
    """Return weekly agenda as a table: days (Mon-Fri) in columns and hours (09:00-17:00) in rows."""
    log("<get_week_agenda>")
    by_slot = {(m["day"], m["time"]): m for m in AGENDA}
    table: list[list[Any]] = []

    # First row: column names
    table.append(["hour", *WEEK_DAYS])

    for hour in HOURS_BY_DAY[WEEK_DAYS[0]]:
        row: list[Any] = [hour]
        for day in WEEK_DAYS:
            m = by_slot.get((day, hour))
            if m:
                row.append({
                    "meeting_id": m["id"],
                    "meeting_name": m["meeting_name"],
                    "customer_name": m["customer_name"],
                    "company": m["company"],
                    "status": m["status"],
                })
            else:
                row.append({
                    "meeting_id": None,
                    "meeting_name": None,
                    "customer_name": None,
                    "company": None,
                    "status": "free",
                })
        table.append(row)

    return table


@mcp.tool()
def list_customers(score: Optional[int] = None) -> list[dict[str, Any]]:
    """List customers, optionally filtered by score (1..10)."""
    log(f"<list_customers> score={score}")
    if score is not None and (score < 1 or score > 10):
        raise ValueError("score must be between 1 and 10")

    customers = CUSTOMERS
    if score is not None:
        customers = [c for c in CUSTOMERS if c["score"] == score]

    return [
        {
            "customer_id": c["id"],
            "name": c["name"],
            "company": c["company"],
            "location": c["location"],
            "interest": c["interest"],
            "score": c["score"],
        }
        for c in customers
    ]


@mcp.tool()
def next_meeting(customer_name: str) -> dict[str, Any]:
    """Get next planned meeting details for one single customer, including notes and customer profile."""
    log(f"<next_meeting> customer_name={customer_name}")
    customer = _customer_from_name(customer_name)
    if not customer:
        raise ValueError(f"Unknown customer: {customer_name}")

    meetings = [
        m for m in sorted(AGENDA, key=_meeting_sort_key)
        if m["customer_id"] == customer["id"] and m["status"] == "planned"
    ]
    if not meetings:
        return {
            "message": "No planned meeting for this customer.",
            "customer": {
                "name": customer["name"],
                "company": customer["company"],
                "location": customer["location"],
                "interest": customer["interest"],
                "score": customer["score"],
            },
        }

    m = meetings[0]
    return {
        "meeting": {
            "meeting_id": m["id"],
            "day": m["day"],
            "time": m["time"],
            "meeting_name": m["meeting_name"],
            "meeting_goal": m["meeting_goal"],
            "previous_notes": m["previous_notes"],
        },
        "customer": {
            "customer_id": customer["id"],
            "name": customer["name"],
            "company": customer["company"],
            "location": customer["location"],
            "interest": customer["interest"],
            "score": customer["score"],
        },
    }


@mcp.tool()
def record_meeting(customer_name: str, meeting_details: str, result: str) -> dict[str, Any]:
    """Record details for the customer's next planned meeting; increase score by +2 when result is good."""
    log(f"<record_meeting> customer_name={customer_name}, result={result}")
    customer = _customer_from_name(customer_name)
    if not customer:
        raise ValueError(f"Unknown customer: {customer_name}")

    planned = [
        m for m in sorted(AGENDA, key=_meeting_sort_key)
        if m["customer_id"] == customer["id"] and m["status"] == "planned"
    ]
    if not planned:
        raise ValueError("No planned next_meeting for this customer.")

    meeting = planned[0]
    meeting["recorded_details"] = meeting_details
    meeting["status"] = "done"
    meeting["previous_notes"] = meeting_details
    LAST_RECORDED_MEETING_BY_CUSTOMER[customer["id"]] = meeting["id"]

    score_before = customer["score"]
    if result.strip().lower() in {"good", "won", "positive", "success", "successful"}:
        idx = _customer_index(customer["id"])
        if idx is not None:
            CUSTOMERS[idx]["score"] = min(10, CUSTOMERS[idx]["score"] + 2)
            customer = CUSTOMERS[idx]

    # carry notes to next meeting (if any)
    upcoming = [
        m for m in sorted(AGENDA, key=_meeting_sort_key)
        if m["customer_id"] == customer["id"] and m["status"] == "planned"
    ]
    if upcoming:
        upcoming[0]["previous_notes"] = meeting_details

    return {
        "status": "recorded",
        "recorded_meeting_id": meeting["id"],
        "customer_name": customer["name"],
        "score_before": score_before,
        "score_after": customer["score"],
        "details": meeting_details,
    }


@mcp.tool()
def check_customer_status(customer_name: str) -> dict[str, Any]:
    """Check latest customer status and details after a meeting is recorded."""
    log(f"<check_customer_status> customer_name={customer_name}")
    customer = _customer_from_name(customer_name)
    if not customer:
        raise ValueError(f"Unknown customer: {customer_name}")

    last_meeting_id = LAST_RECORDED_MEETING_BY_CUSTOMER.get(customer["id"])
    last_meeting = next((m for m in AGENDA if m["id"] == last_meeting_id), None)

    upcoming = [
        m for m in sorted(AGENDA, key=_meeting_sort_key)
        if m["customer_id"] == customer["id"] and m["status"] == "planned"
    ]

    return {
        "customer": {
            "customer_id": customer["id"],
            "name": customer["name"],
            "company": customer["company"],
            "location": customer["location"],
            "interest": customer["interest"],
            "score": customer["score"],
        },
        "last_recorded_meeting": (
            {
                "meeting_id": last_meeting["id"],
                "day": last_meeting["day"],
                "time": last_meeting["time"],
                "meeting_name": last_meeting["meeting_name"],
                "details": last_meeting["recorded_details"],
            }
            if last_meeting
            else None
        ),
        "next_planned_meeting": (
            {
                "meeting_id": upcoming[0]["id"],
                "day": upcoming[0]["day"],
                "time": upcoming[0]["time"],
                "meeting_name": upcoming[0]["meeting_name"],
                "meeting_goal": upcoming[0]["meeting_goal"],
            }
            if upcoming
            else None
        ),
    }


@mcp.tool()
def add_customer_in_free_slot(customer_name: str, meeting_goal: Optional[str] = None) -> dict[str, Any]:
    """Schedule a customer in the earliest free agenda slot (Monday-Friday). Ask for end-user approval before to call this functions. Show the approval in a form format."""
    log(f"<add_customer_in_free_slot> customer_name={customer_name}")
    customer = _customer_from_name(customer_name)
    if not customer:
        raise ValueError(f"Unknown customer: {customer_name}")

    slots = _free_slots()
    if not slots:
        return {
            "status": "no_free_slot",
            "message": "No free slot available in the current Monday-Friday agenda.",
        }

    slot = slots[0]
    new_id = f"m{len(AGENDA) + 1}"
    goal = meeting_goal or f"Follow-up on {customer['interest']} and define next sales action."
    meeting_name = f"Customer follow-up with {customer['company']}"

    AGENDA.append(
        {
            "id": new_id,
            "day": slot["day"],
            "time": slot["time"],
            "meeting_name": meeting_name,
            "meeting_goal": goal,
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "company": customer["company"],
            "status": "planned",
            "previous_notes": "No previous meeting recorded yet.",
            "recorded_details": None,
        }
    )

    return {
        "status": "scheduled",
        "meeting": {
            "meeting_id": new_id,
            "day": slot["day"],
            "time": slot["time"],
            "meeting_name": meeting_name,
            "meeting_goal": goal,
            "customer_name": customer["name"],
            "company": customer["company"],
        },
    }

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
