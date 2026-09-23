"""Generate the executive-style interactive HTML compliance report."""

import html
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """Render a compliance report with executive summary and control drilldowns."""

    def generate(self, report, config_file: str = "", output_path: str = "") -> str:
        content = self._build_report(report, config_file)
        if output_path:
            Path(output_path).write_text(content, encoding="utf-8")
            logger.info("HTML report saved: %s", output_path)
        return content

    def _build_report(self, report, config_file: str) -> str:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        config_name = Path(config_file).name if config_file else "N/A"
        failed = report.failed_rules
        score_color = self._pct_color(report.overall_percentage)
        category_rows = "".join(self._category_row(name, score) for name, score in report.category_scores.items())
        failed_rows = "".join(self._control_row(result) for result in report.failed_results)
        all_rows = "".join(self._control_row(result) for result in report.results)

        return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Auditoria CIS FortiGate | {html.escape(config_name)}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap');
:root {{ --navy:#0a1628; --blue:#0099d6; --cyan:#38bdf8; --ink:#1e293b; --muted:#64748b; --line:#e2e8f0; --paper:#f0f4f8; --green:#16a34a; --amber:#f59e0b; --orange:#f97316; --red:#ef4444; }}
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:Inter,sans-serif; background:var(--paper); color:var(--ink); font-size:14px; line-height:1.55; }}
.header {{ background:#fff; border-bottom:2px solid var(--line); padding:16px 48px; position:sticky; top:0; z-index:5; display:flex; justify-content:space-between; align-items:center; gap:20px; }} .header strong {{ display:block; font-size:12px; }} .header small {{ color:#94a3b8; }}
.shell {{ max-width:1280px; margin:auto; padding:42px 48px; }}
.section {{ margin-bottom:42px; }} .section-heading {{ display:flex; align-items:center; gap:14px; padding-bottom:14px; margin-bottom:20px; border-bottom:2px solid #f1f5f9; }} .section-number {{ background:linear-gradient(135deg,var(--navy),var(--blue)); color:#fff; border-radius:8px; width:36px; height:36px; display:grid; place-items:center; font:700 12px 'JetBrains Mono'; }} .section-heading h2 {{ font-size:19px; }} .section-heading p {{ color:var(--muted); font-size:12px; }}
.summary {{ background:#f0f9ff; border-left:4px solid var(--blue); padding:20px 24px; border-radius:10px; color:#334155; margin-bottom:20px; }} .cards {{ display:grid; gap:16px; }} .cards-4 {{ grid-template-columns:repeat(4,1fr); }} .card,.panel {{ background:#fff; border:1px solid var(--line); border-radius:12px; box-shadow:0 1px 3px #0000000d; }} .card {{ padding:20px; }} .metric {{ font:800 34px 'JetBrains Mono'; }} .label {{ color:var(--muted); font-size:10px; font-weight:800; letter-spacing:1px; text-transform:uppercase; margin-top:7px; }} .note {{ color:#94a3b8; font-size:11px; margin-top:3px; }} .bar {{ height:6px; background:#f1f5f9; border-radius:4px; overflow:hidden; margin-top:12px; }} .bar i {{ display:block; height:100%; border-radius:4px; }} .panel {{ padding:24px; margin-bottom:18px; }}
.alert {{ padding:13px 17px; border-radius:9px; margin:12px 0; border-left:4px solid; font-size:13px; }} .alert-warn {{ background:#fffbeb; border-color:var(--amber); color:#78350f; }} .alert-ok {{ background:#f0fdf4; border-color:var(--green); color:#14532d; }}
.table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:10px; }} table {{ width:100%; border-collapse:collapse; background:#fff; }} th {{ background:#f8fafc; color:var(--muted); padding:11px 14px; text-align:left; font-size:10px; text-transform:uppercase; letter-spacing:1px; white-space:nowrap; }} td {{ padding:11px 14px; border-top:1px solid #f1f5f9; vertical-align:top; font-size:13px; }} tr:hover {{ background:#f8fafc; }} .mono {{ font-family:'JetBrains Mono'; font-size:12px; }} .badge {{ display:inline-block; padding:3px 9px; border-radius:20px; font-size:10px; font-weight:800; text-transform:uppercase; }} .pass {{ background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0; }} .fail {{ background:#fef2f2;color:#dc2626;border:1px solid #fecaca; }} .critical {{ color:#dc2626; }} .high {{ color:#ea580c; }} .medium {{ color:#2563eb; }} .low {{ color:#16a34a; }}
.controls {{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:15px; }} input,.filter {{ border:1px solid var(--line); border-radius:8px; background:#fff; padding:9px 13px; color:var(--ink); }} input {{ flex:1; min-width:220px; }} .filter {{ cursor:pointer; }} .filter.active,.filter:hover {{ background:var(--blue); color:#fff; border-color:var(--blue); }} details {{ background:#f8fafc; border-top:1px solid var(--line); padding:11px 14px; }} details summary {{ cursor:pointer; font-weight:700; color:#075985; }} .detail-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:12px; }} .detail-grid div {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:10px; }} .detail-grid b {{ display:block; color:var(--muted); font-size:10px; text-transform:uppercase; margin-bottom:4px; }} .footer {{ background:var(--navy); color:#94a3b8; text-align:center; padding:24px; font-size:11px; }}
@media(max-width:800px) {{ .cards-4 {{ grid-template-columns:repeat(2,1fr); }} .shell {{ padding:28px 18px; }} .header {{ padding:14px 18px; }} .detail-grid {{ grid-template-columns:1fr; }} }}
@media print {{ .header {{ position:relative; }} .controls {{ display:none; }} details[open] {{ break-inside:avoid; }} }}
</style>
</head>
<body>
<header class="header"><div><strong>FortiGate CIS Audit</strong><small>{html.escape(config_name)}</small></div><div><strong>Risco: {html.escape(report.risk_rating)}</strong><small>Score ponderado: {report.weighted_score}%</small></div></header>
<main class="shell">
<section class="section"><div class="section-heading"><span class="section-number">01</span><div><h2>Resumo Executivo</h2><p>Visão consolidada da postura de segurança</p></div></div><div class="summary">A avaliação analisou <b>{report.total_rules} controles CIS</b>. Foram aprovados <b>{report.passed_rules}</b> controles e identificadas <b>{report.failed_rules} oportunidades de adequação</b>. O risco consolidado foi classificado como <b>{html.escape(report.risk_rating)}</b>.</div><div class="cards cards-4"><div class="card"><div class="metric" style="color:{score_color}">{report.overall_percentage}%</div><div class="label">Conformidade geral</div><div class="note">{report.passed_rules}/{report.total_rules} controles</div><div class="bar"><i style="width:{report.overall_percentage}%;background:{score_color}"></i></div></div><div class="card"><div class="metric" style="color:{self._pct_color(report.level1_percentage)}">{report.level1_percentage}%</div><div class="label">Level 1</div><div class="note">{report.level1_passed}/{report.level1_total} aprovados</div></div><div class="card"><div class="metric" style="color:{self._pct_color(report.level2_percentage)}">{report.level2_percentage}%</div><div class="label">Level 2</div><div class="note">{report.level2_passed}/{report.level2_total} aprovados</div></div><div class="card"><div class="metric" style="color:{score_color}">{report.weighted_score}%</div><div class="label">Score ponderado</div><div class="note">Risco: {html.escape(report.risk_rating)}</div></div></div></section>
<section class="section"><div class="section-heading"><span class="section-number">02</span><div><h2>Severidade e Prioridades</h2><p>Controles organizados por impacto</p></div></div><div class="cards cards-4"><div class="card"><div class="metric critical">{report.critical_total-report.critical_passed}</div><div class="label">Falhas críticas</div><div class="note">{report.critical_passed}/{report.critical_total} aprovados</div></div><div class="card"><div class="metric high">{report.high_total-report.high_passed}</div><div class="label">Falhas altas</div><div class="note">{report.high_passed}/{report.high_total} aprovados</div></div><div class="card"><div class="metric medium">{report.medium_total-report.medium_passed}</div><div class="label">Falhas médias</div><div class="note">{report.medium_passed}/{report.medium_total} aprovados</div></div><div class="card"><div class="metric low">{report.low_total-report.low_passed}</div><div class="label">Falhas baixas</div><div class="note">{report.low_passed}/{report.low_total} aprovados</div></div></div>{('<div class="alert alert-ok">Todos os controles foram aprovados.</div>' if not failed else '<div class="alert alert-warn"><b>Ação prioritária:</b> revisar os controles críticos e altos listados no drilldown abaixo.</div>')}</section>
<section class="section"><div class="section-heading"><span class="section-number">03</span><div><h2>Conformidade por Categoria</h2><p>Distribuição da postura de segurança</p></div></div><div class="panel"><div class="table-wrap"><table><thead><tr><th>Categoria</th><th>Total</th><th>Aprovados</th><th>Falhas</th><th>Score</th></tr></thead><tbody>{category_rows}</tbody></table></div></div></section>
<section class="section"><div class="section-heading"><span class="section-number">04</span><div><h2>Controles e Drilldowns</h2><p>Busca, filtros e detalhes de auditoria por controle</p></div></div><div class="panel"><div class="controls"><input id="searchInput" placeholder="Pesquisar regra, título ou valor..." oninput="applyFilters()"><button class="filter active" onclick="setStatus('all',this)">Todos</button><button class="filter" onclick="setStatus('PASS',this)">Aprovados</button><button class="filter" onclick="setStatus('FAIL',this)">Falhas</button><button class="filter" onclick="setSeverity('Critical',this)">Crítico</button><button class="filter" onclick="setSeverity('High',this)">Alto</button></div><div class="table-wrap"><table id="controlsTable"><thead><tr><th>ID</th><th>Controle</th><th>Level</th><th>Severidade</th><th>Status</th><th>Valor atual</th></tr></thead><tbody>{all_rows}</tbody></table></div></div></section>
<section class="section"><div class="section-heading"><span class="section-number">05</span><div><h2>Falhas e Remediação</h2><p>Itens que exigem acompanhamento técnico</p></div></div><div class="panel"><div class="table-wrap"><table><thead><tr><th>ID</th><th>Controle</th><th>Severidade</th><th>Atual</th><th>Esperado</th><th>Remediação</th></tr></thead><tbody>{failed_rows or '<tr><td colspan="6">Nenhuma falha identificada.</td></tr>'}</tbody></table></div></div></section>
</main><footer class="footer"><b>Solor MSS FortiGate Audit</b> · Relatório interativo · Gerado em {timestamp}</footer>
<script>
let statusFilter='all',severityFilter='all';
function applyFilters(){{const q=document.getElementById('searchInput').value.toLowerCase();document.querySelectorAll('#controlsTable tbody tr.control-row').forEach(r=>{{const okText=!q||r.textContent.toLowerCase().includes(q);const okStatus=statusFilter==='all'||r.dataset.status===statusFilter;const okSeverity=severityFilter==='all'||r.dataset.severity===severityFilter;r.style.display=okText&&okStatus&&okSeverity?'':'none';}})}}
function clearActive(){{document.querySelectorAll('.filter').forEach(b=>b.classList.remove('active'));}}
function setStatus(v,b){{statusFilter=v;clearActive();b.classList.add('active');applyFilters();}}
function setSeverity(v,b){{severityFilter=severityFilter===v?'all':v;clearActive();if(severityFilter!=='all')b.classList.add('active');applyFilters();}}
</script></body></html>'''

    def _category_row(self, name, score):
        pct = score.percentage
        return f'<tr><td><b>{html.escape(name)}</b></td><td>{score.total}</td><td>{score.passed}</td><td>{score.failed}</td><td><div class="bar"><i style="width:{pct}%;background:{self._pct_color(pct)}"></i></div><span class="mono">{pct}%</span></td></tr>'

    def _control_row(self, result):
        status = "PASS" if result.passed else "FAIL"
        status_class = "pass" if result.passed else "fail"
        severity = result.severity.value
        details = f'<details><summary>Ver evidências, expectativa e remediação</summary><div class="detail-grid"><div><b>Valor atual</b>{html.escape(result.actual_value)}</div><div><b>Esperado</b>{html.escape(result.expected_value)}</div><div><b>Remediação</b>{html.escape(result.remediation)}</div></div></details>'
        return f'<tr class="control-row" data-status="{status}" data-severity="{html.escape(severity)}"><td class="mono">{html.escape(result.rule_id)}</td><td><b>{html.escape(result.title)}</b>{details}</td><td>L{result.level.value}</td><td class="{severity.lower()}">{html.escape(severity)}</td><td><span class="badge {status_class}">{status}</span></td><td>{html.escape(result.actual_value)}</td></tr>'

    def _pct_color(self, pct):
        if pct >= 80:
            return "#16a34a"
        if pct >= 60:
            return "#f59e0b"
        if pct >= 40:
            return "#f97316"
        return "#ef4444"
