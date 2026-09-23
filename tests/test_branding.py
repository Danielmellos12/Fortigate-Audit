from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_no_branding_strings_in_core_files():
    files = [
        PROJECT_ROOT / "run_audit.py",
        PROJECT_ROOT / "readme.md",
        PROJECT_ROOT / "cis_benchmark/__init__.py",
        PROJECT_ROOT / "cis_benchmark/reporting/html_report.py",
        PROJECT_ROOT / "cis_benchmark/reporting/json_report.py",
    ]
    combined = "\n".join(p.read_text(encoding="utf-8") for p in files)

    forbidden = [
        "FortiGate CIS Benchmark Compliance Auditor",
        "FortiGate CIS Benchmark Checker",
        "FORTIGATE SECURITY BASELINE",
        "Author: Priyam Patel",
        "Priyam Patel",
    ]

    for item in forbidden:
        assert item not in combined
