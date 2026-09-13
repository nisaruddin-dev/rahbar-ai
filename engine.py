"""
Rahbar AI — Deterministic Decision Engine

Architecture rule:
    This file contains LOGIC ONLY. It never imports Streamlit.
    It is called by app.py. It never calls app.py.

Every public function returns:
    {
        "ok":      bool,
        "error":   str | None,
        "raw":     dict,
        "summary": dict,
    }

To add a new decision rule:
    Write a new function that follows this contract.
    Register it in the appropriate helper below if needed.
    Do not modify app.py unless you need to display a new output.
"""

from datetime import date, datetime
from typing import Any

from data.universities import UNIVERSITIES


# ---------------------------------------------------------------------------
# Input constraints — absolute mark maximums per Pakistani board standards
# ---------------------------------------------------------------------------

MATRIC_MAX = 1100     # SSC total marks (Punjab/Federal boards, standard)
HSSC_PART1_MAX = 550  # FSc Part-I total marks (standard)
TEST_MAX = {
    "NUST": 200,      # NET
    "UET Taxila": 400,# ECAT
    "FAST": 100,      # FAST entry test
}


# ---------------------------------------------------------------------------
# Public function 1 — validate_inputs
# ---------------------------------------------------------------------------

def validate_inputs(
    university: str,
    matric: float,
    hssc: float,
    test: float,
) -> dict[str, Any]:
    """
    Validate the student's marks and university selection.

    Returns {ok, error, raw, summary}.
    """
    try:
        # University must exist
        if university not in UNIVERSITIES:
            return {
                "ok": False,
                "error": f"Unsupported university: '{university}'. "
                         f"Supported: {', '.join(UNIVERSITIES.keys())}.",
                "raw": {},
                "summary": {},
            }

        # Marks must be non-negative numbers
        for label, value in [("Matric", matric), ("FSc Part-I", hssc), ("Entry Test", test)]:
            if not isinstance(value, (int, float)):
                return {
                    "ok": False,
                    "error": f"{label} marks must be a number.",
                    "raw": {},
                    "summary": {},
                }
            if value < 0:
                return {
                    "ok": False,
                    "error": f"{label} marks cannot be negative.",
                    "raw": {},
                    "summary": {},
                }

        # Marks must not exceed board maximums
        test_max = TEST_MAX.get(university, 100)
        if matric > MATRIC_MAX:
            return {
                "ok": False,
                "error": f"Matric marks cannot exceed {MATRIC_MAX}.",
                "raw": {"matric_max": MATRIC_MAX},
                "summary": {},
            }
        if hssc > HSSC_PART1_MAX:
            return {
                "ok": False,
                "error": f"FSc Part-I marks cannot exceed {HSSC_PART1_MAX}.",
                "raw": {"hssc_max": HSSC_PART1_MAX},
                "summary": {},
            }
        if test > test_max:
            return {
                "ok": False,
                "error": f"{university} entry test marks cannot exceed {test_max}.",
                "raw": {"test_max": test_max},
                "summary": {},
            }

        # All checks passed
        return {
            "ok": True,
            "error": None,
            "raw": {
                "matric_max": MATRIC_MAX,
                "hssc_max": HSSC_PART1_MAX,
                "test_max": test_max,
            },
            "summary": {
                "university": university,
                "matric_pct": round(matric / MATRIC_MAX * 100, 2),
                "hssc_pct": round(hssc / HSSC_PART1_MAX * 100, 2),
                "test_pct": round(test / test_max * 100, 2),
            },
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Validation error: {e}",
            "raw": {},
            "summary": {},
        }


# ---------------------------------------------------------------------------
# Public function 2 — calculate_aggregate
# ---------------------------------------------------------------------------

def calculate_aggregate(
    university: str,
    matric: float,
    hssc: float,
    test: float,
) -> dict[str, Any]:
    """
    Compute the university aggregate using the verified formula.

    Uses absolute marks internally, converts to percentages, applies weights.
    Returns {ok, error, raw, summary}.
    """
    try:
        if university not in UNIVERSITIES:
            return {
                "ok": False,
                "error": f"Unsupported university: '{university}'.",
                "raw": {},
                "summary": {},
            }

        record = UNIVERSITIES[university]
        formula = record["formula"]
        test_max = TEST_MAX.get(university, 100)

        # Convert absolute marks to percentages
        matric_pct = matric / MATRIC_MAX * 100
        hssc_pct = hssc / HSSC_PART1_MAX * 100
        test_pct = test / test_max * 100

        # Map formula keys to percentage values
        components: dict[str, float] = {}
        weighted: dict[str, float] = {}

        for key, weight in formula.items():
            if key in ("ssc", "matric"):
                pct = matric_pct
            elif key in ("hssc", "hssc_part1"):
                pct = hssc_pct
            elif key in ("net", "ecat", "test"):
                pct = test_pct
            else:
                return {
                    "ok": False,
                    "error": f"Unknown formula component: '{key}' for {university}.",
                    "raw": {"formula": formula},
                    "summary": {},
                }

            components[key] = round(pct, 2)
            weighted[key] = round(pct * weight, 2)

        aggregate = round(sum(weighted.values()), 2)

        return {
            "ok": True,
            "error": None,
            "raw": {
                "formula_used": formula,
                "components_pct": components,
                "components_weighted": weighted,
            },
            "summary": {
                "university": university,
                "aggregate": aggregate,
                "formula_string": record["formula_string"],
            },
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Calculation error: {e}",
            "raw": {},
            "summary": {},
        }


# ---------------------------------------------------------------------------
# Public function 3 — get_deadline_status
# ---------------------------------------------------------------------------

def get_deadline_status(university: str) -> dict[str, Any]:
    """
    Compute the deadline status from the deadline date.

    Status values: Open / Approaching / Closed / Extended.
    'Approaching' means the deadline is within 7 days from today.
    'Extended' is reserved for future cycles where an extension date is recorded.

    Returns {ok, error, raw, summary}.
    """
    try:
        if university not in UNIVERSITIES:
            return {
                "ok": False,
                "error": f"Unsupported university: '{university}'.",
                "raw": {},
                "summary": {},
            }

        record = UNIVERSITIES[university]
        deadline_str = record["deadline"]
        deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        today = date.today()
        days_remaining = (deadline_date - today).days

        if days_remaining < 0:
            status = "Closed"
            message = f"Deadline was {deadline_str}. Check the official portal for extension notices."
        elif days_remaining <= 7:
            status = "Approaching"
            message = f"Only {days_remaining} days left. Apply now before it closes."
        else:
            status = "Open"
            message = f"{days_remaining} days remaining. Plan your application soon."

        return {
            "ok": True,
            "error": None,
            "raw": {
                "deadline": deadline_str,
                "today": today.isoformat(),
                "days_remaining": days_remaining,
            },
            "summary": {
                "university": university,
                "status": status,
                "message": message,
                "deadline": deadline_str,
            },
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Deadline computation error: {e}",
            "raw": {},
            "summary": {},
        }


# ---------------------------------------------------------------------------
# Public function 4 — get_document_checklist
# ---------------------------------------------------------------------------

def get_document_checklist(university: str) -> dict[str, Any]:
    """
    Return the list of documents required for the university.

    Returns {ok, error, raw, summary}.
    """
    try:
        if university not in UNIVERSITIES:
            return {
                "ok": False,
                "error": f"Unsupported university: '{university}'.",
                "raw": {},
                "summary": {},
            }

        docs = UNIVERSITIES[university]["documents"]

        return {
            "ok": True,
            "error": None,
            "raw": {"documents": docs, "count": len(docs)},
            "summary": {
                "university": university,
                "documents": docs,
                "count": len(docs),
            },
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Checklist error: {e}",
            "raw": {},
            "summary": {},
        }


# ---------------------------------------------------------------------------
# Public function 5 — get_next_action
# ---------------------------------------------------------------------------

def get_next_action(
    university: str,
    aggregate: float,
    deadline_status: str,
) -> dict[str, Any]:
    """
    Produce a deterministic next action based on university + aggregate + deadline.

    This is the "What Should I Do Next?" engine — the defining UX of Rahbar AI.

    Returns {ok, error, raw, summary}.
    """
    try:
        if university not in UNIVERSITIES:
            return {
                "ok": False,
                "error": f"Unsupported university: '{university}'.",
                "raw": {},
                "summary": {},
            }

        record = UNIVERSITIES[university]
        portal = record["source_url"]
        part1_ok = record["part1_allowed"]
        deadline_str = record["deadline"]

        actions: list[str] = []

        # Action 1 — deadline-driven
        if deadline_status == "Open":
            actions.append(
                f"Visit the official {university} admission portal and begin your application."
            )
        elif deadline_status == "Approaching":
            actions.append(
                f"URGENT: Apply today or tomorrow at {university}. Deadline is {deadline_str}."
            )
        elif deadline_status == "Closed":
            actions.append(
                f"Check the official {university} portal for extension notices or next-cycle dates."
            )
        else:
            actions.append(f"Verify the {university} deadline at the official portal.")

        # Action 2 — Part-I allowance
        if part1_ok:
            actions.append(
                f"You can apply with FSc Part-I marks at {university}. "
                f"Do not wait for your final result."
            )
        else:
            actions.append(
                f"Confirm result requirements at the {university} portal before applying."
            )

        # Action 3 — preparation
        actions.append(
            f"Prepare the required documents listed in the checklist before applying."
        )

        return {
            "ok": True,
            "error": None,
            "raw": {
                "aggregate": aggregate,
                "deadline_status": deadline_status,
                "part1_allowed": part1_ok,
            },
            "summary": {
                "university": university,
                "actions": actions,
                "portal_url": portal,
            },
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Next-action error: {e}",
            "raw": {},
            "summary": {},
        }