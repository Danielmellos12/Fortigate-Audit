"""
Solor MSS FortiGate Audit Dashboard
==================================
Flask-based web UI for running CIS compliance audits.
"""

import os
import sys
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cis_benchmark.config_parser import FortiGateConfigParser
from cis_benchmark.rules import get_all_rules, get_level1_rules, get_level2_rules
from cis_benchmark.scoring import ComplianceScorer
from cis_benchmark.remediation import RemediationEngine
from cis_benchmark.reporting import HTMLReportGenerator, JSONReportGenerator, PDFReportGenerator

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['SECRET_KEY'] = os.urandom(24).hex()

# Store the latest audit result in memory
latest_audit = {"report": None, "config_file": "", "timestamp": None}

UPLOAD_FOLDER = tempfile.mkdtemp(prefix="fortigate_audit_")


def run_audit(config_path: str, level_filter: str = "all"):
    """Run CIS audit on a config file."""
    parser = FortiGateConfigParser()
    config = parser.parse_file(config_path)

    if level_filter == "1":
        rules = get_level1_rules()
    elif level_filter == "2":
        rules = get_level2_rules()
    else:
        rules = get_all_rules()

    results = []
    for rule in rules:
        result = rule.evaluate(config)
        results.append(result)

    scorer = ComplianceScorer()
    report = scorer.calculate(results)
    return report


@app.route('/')
def index():
    """Dashboard home page."""
    return render_template('dashboard.html', audit=latest_audit)


@app.route('/upload', methods=['POST'])
def upload_config():
    """Upload and audit a FortiGate config file."""
    if 'config_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['config_file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Validate filename (security)
    filename = file.filename.replace('..', '').replace('/', '').replace('\\', '')
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    # Save uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        level_filter = request.form.get('level', 'all')
        report = run_audit(filepath, level_filter)

        latest_audit["report"] = report
        latest_audit["config_file"] = filename
        latest_audit["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except OSError:
            pass


@app.route('/api/audit', methods=['POST'])
def api_audit():
    """API endpoint for audit - returns JSON."""
    if 'config_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['config_file']
    filename = file.filename.replace('..', '').replace('/', '').replace('\\', '')
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        level_filter = request.form.get('level', 'all')
        report = run_audit(filepath, level_filter)
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(filepath)
        except OSError:
            pass


@app.route('/download/<format_type>')
def download_report(format_type):
    """Download report in specified format."""
    if not latest_audit["report"]:
        return jsonify({"error": "No audit results available. Run an audit first."}), 400

    report = latest_audit["report"]
    config_file = latest_audit["config_file"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format_type == "html":
        gen = HTMLReportGenerator()
        output_path = os.path.join(UPLOAD_FOLDER, f"CIS_Report_{timestamp}.html")
        gen.generate(report, config_file=config_file, output_path=output_path)
        return send_file(output_path, as_attachment=True, download_name=f"CIS_Report_{timestamp}.html")

    elif format_type == "json":
        gen = JSONReportGenerator()
        output_path = os.path.join(UPLOAD_FOLDER, f"CIS_Report_{timestamp}.json")
        gen.generate(report, config_file=config_file, output_path=output_path)
        return send_file(output_path, as_attachment=True, download_name=f"CIS_Report_{timestamp}.json")

    elif format_type == "pdf":
        html_gen = HTMLReportGenerator()
        html_content = html_gen.generate(report, config_file=config_file)
        pdf_gen = PDFReportGenerator()
        output_path = os.path.join(UPLOAD_FOLDER, f"CIS_Report_{timestamp}.pdf")
        pdf_gen.generate(html_content, output_path)
        actual_file = output_path if os.path.exists(output_path) else output_path.replace('.pdf', '_report.html')
        return send_file(actual_file, as_attachment=True)

    elif format_type == "remediation":
        engine = RemediationEngine()
        script = engine.generate_script(report.failed_results, dry_run=True)
        output_path = os.path.join(UPLOAD_FOLDER, f"Remediation_{timestamp}.txt")
        engine.save_script(script, output_path)
        return send_file(output_path, as_attachment=True, download_name=f"Remediation_{timestamp}.txt")

    return jsonify({"error": "Invalid format"}), 400


def create_app():
    """Application factory."""
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
