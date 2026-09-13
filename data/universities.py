"""
Rahbar AI — Verified University Data Registry

Architecture rule:
    This file contains DATA ONLY. No logic. No imports from engine.py or app.py.

To add a new university:
    Append a new key to UNIVERSITIES. Do not modify any other file.

Every record must follow the same shape:
    {
        "name":              str,
        "programs":          list[str],
        "deadline":          str,          # ISO date "YYYY-MM-DD"
        "part1_allowed":     bool,
        "formula":           dict[str, float],   # weights sum to 1.0
        "formula_string":    str,          # human-readable formula
        "documents":         list[str],
        "source_url":        str,
        "last_verified":     str,          # ISO date "YYYY-MM-DD"
        "verification_note": str | None,   # None if fully verified
    }
"""

UNIVERSITIES: dict[str, dict] = {
    "NUST": {
        "name": "NUST",
        "programs": ["BSCS", "BSSE"],
        "deadline": "2026-08-30",
        "part1_allowed": True,
        "formula": {
            "net": 0.75,       # NET entry test
            "hssc": 0.15,      # FSc Part-I / HSSC
            "ssc": 0.10,       # Matric / SSC
        },
        "formula_string": "NET 75% + HSSC 15% + SSC 10%",
        "documents": [
            "SSC Marksheet",
            "HSSC Part-I Marksheet",
            "CNIC/B-Form",
            "Photograph",
        ],
        "source_url": "https://nust.edu.pk/admissions/",
        "last_verified": "2026-09-13",
        "verification_note": None,
    },
    "UET Taxila": {
        "name": "UET Taxila",
        "programs": ["BSCS", "BSSE"],
        "deadline": "2026-08-25",
        "part1_allowed": True,
        "formula": {
            "hssc_part1": 0.50,   # FSc Part-I
            "ecat": 0.33,         # ECAT entry test
            "ssc": 0.17,          # Matric / SSC
        },
        "formula_string": "HSSC-I 50% + ECAT 33% + SSC 17%",
        "documents": [
            "SSC Marksheet",
            "HSSC Part-I Marksheet",
            "CNIC/B-Form",
            "Photograph",
            "Domicile",
        ],
        "source_url": "https://admissions.uettaxila.edu.pk/",
        "last_verified": "2026-09-13",
        "verification_note": (
            "Verify deadline and formula at the official UET Taxila admission portal. "
            "Data reflects most recent available cycle."
        ),
    },
    "FAST": {
        "name": "FAST",
        "programs": ["BSCS", "BSSE"],
        "deadline": "2026-06-30",
        "part1_allowed": True,
        "formula": {
            "test": 0.50,      # FAST entry test
            "hssc": 0.40,      # FSc Part-I / HSSC
            "ssc": 0.10,       # Matric / SSC
        },
        "formula_string": "Test 50% + HSSC 40% + SSC 10%",
        "documents": [
            "SSC Marksheet",
            "HSSC Part-I Marksheet",
            "CNIC/B-Form",
            "Photograph",
        ],
        "source_url": "https://www.nu.edu.pk/Admissions/",
        "last_verified": "2026-09-13",
        "verification_note": (
            "Verify deadline and formula at the official FAST-NU admission portal. "
            "Data reflects most recent available cycle."
        ),
    },
}


# -- Helper to list supported universities (used by app.py for the dropdown) --
SUPPORTED_UNIVERSITIES: list[str] = list(UNIVERSITIES.keys())