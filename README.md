# Solor MSS FortiGate Audit

FortiGate CIS benchmark auditing tool for the Solor MSS team.

## Features

- **56 CIS Controls** – 35 Level 1 (Basic) + 21 Level 2 (Advanced)
- **Structured Config Parser** – Parses FortiGate `.conf` backups into structured data
- **Compliance Scoring** – Overall %, Level 1/L2 scores, severity-weighted scoring
- **Multi-Format Reports** – HTML (dark-mode enterprise), JSON (SIEM), PDF
- **Web Dashboard** – Flask-based UI with upload, scores, filters, downloads
- **Remediation Engine** – Auto-generates FortiGate CLI scripts with dry-run mode
- **Threaded Execution** – Concurrent rule evaluation for performance
- **Unit Tested** – 57+ tests covering parser, rules, and scoring

## Quick Start

```bash
# Install
pip install -r requirements.txt

# CLI Audit (use a local FortiGate configuration file)
python run_audit.py /caminho/local/config.conf

# With options
python run_audit.py config.conf --format html,json --level 1 --output-dir ./reports

# Web Dashboard
python run_audit.py --web
```

## Project Structure

```
├── cis_benchmark/              # Core CIS engine
│   ├── config_parser.py        # FortiGate config parser
│   ├── scoring.py              # Compliance scoring
│   ├── remediation.py          # CLI remediation scripts
│   ├── rules/                  # CIS benchmark rules
│   │   ├── base.py             # Base rule classes
│   │   ├── level1_rules.py     # 35 Level 1 rules
│   │   └── level2_rules.py     # 21 Level 2 rules
│   └── reporting/              # Report generators
│       ├── html_report.py      # Enterprise HTML report
│       ├── json_report.py      # SIEM-compatible JSON
│       └── pdf_report.py       # PDF (optional weasyprint)
├── web/                        # Web UI dashboard
│   ├── app.py                  # Flask application
│   └── templates/dashboard.html
├── tests/                      # Unit tests
├── docs/                       # Documentation
└── run_audit.py                # CLI entry point
```

## Documentation

- [Architecture](docs/architecture.md) – System overview and module details
- [Rule Mapping](docs/rule_mapping.md) – Complete CIS rule mapping table
- [Usage Guide](docs/usage_guide.md) – Installation, CLI, Web UI, testing

## Ownership

Solor MSS Team

## License

MIT
