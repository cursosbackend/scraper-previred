import os
import json
from datetime import datetime

import pandas as pd

EXCEL_PATH = os.path.join("data", "indicadores_2026.xlsx")
OUTPUT_PATH = os.path.join("docs", "index.html")


def load_data():
    if not os.path.exists(EXCEL_PATH):
        return None, None, None

    indicadores = None
    utm = None
    metas = {}

    try:
        indicadores = pd.read_excel(EXCEL_PATH, sheet_name="Indicadores", index_col=0)
    except Exception:
        pass

    try:
        utm = pd.read_excel(EXCEL_PATH, sheet_name="UTM_UTA")
    except Exception:
        pass

    try:
        meta_df = pd.read_excel(EXCEL_PATH, sheet_name="Metadatos")
        metas = dict(zip(meta_df["clave"], meta_df["valor"]))
    except Exception:
        metas["ultima_actualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return indicadores, utm, metas


def to_serializable(val):
    if isinstance(val, dict | list):
        return json.dumps(val, ensure_ascii=False)
    if pd.isna(val):
        return None
    if isinstance(val, float):
        if val == int(val):
            return int(val)
        return round(val, 2)
    return val


def build_html(indicadores, utm, metas):
    last_update = metas.get("ultima_actualizacion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    indicadores_json = "null"
    utm_json = "null"
    latest = {}

    if indicadores is not None and not indicadores.empty:
        latest_row = indicadores.iloc[-1].to_dict()
        latest = {k: to_serializable(v) for k, v in latest_row.items()}
        indicadores_json = json.dumps(
            {str(idx): {k: to_serializable(v) for k, v in row.items()}
             for idx, row in indicadores.iterrows()},
            ensure_ascii=False,
        )

    if utm is not None and not utm.empty:
        utm_json = json.dumps(
            [{k: to_serializable(v) for k, v in row.items()}
             for _, row in utm.iterrows()],
            ensure_ascii=False,
        )

    # --- HTML template ---
    html = f"""<!DOCTYPE html>
<html lang="es-CL">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Indicadores Previsionales 2026 — Previred + SII</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: 'Inter', system-ui, sans-serif;
    background: #f3f6fc;
    color: #1a2332;
    padding: 24px;
    line-height: 1.5;
}}
.container {{ max-width: 1280px; margin: 0 auto; }}
header {{
    text-align: center;
    margin-bottom: 32px;
    padding: 28px 24px;
    background: linear-gradient(135deg, #003d7a, #0056a8);
    color: #fff;
    border-radius: 16px;
}}
header h1 {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 6px; }}
header p {{ opacity: .85; font-size: .95rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
.card {{
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    text-align: center;
    transition: transform .15s;
}}
.card:hover {{ transform: translateY(-2px); }}
.card .label {{ font-size: .78rem; text-transform: uppercase; letter-spacing: .04em; color: #5b6f87; margin-bottom: 6px; }}
.card .value {{ font-size: 1.55rem; font-weight: 700; color: #003d7a; }}
.card .sub {{ font-size: .8rem; color: #6f7e95; margin-top: 4px; }}
.card.highlight .value {{ color: #c0392b; }}
.section {{ margin-bottom: 32px; }}
.section h2 {{
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #dce3ed;
    color: #003d7a;
}}
.table-wrap {{
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    overflow-x: auto;
}}
table {{ width: 100%; border-collapse: collapse; font-size: .88rem; }}
th {{
    background: #e9eef5;
    color: #1a2332;
    font-weight: 600;
    text-align: left;
    padding: 12px 14px;
    white-space: nowrap;
}}
td {{ padding: 10px 14px; border-top: 1px solid #eef2f7; }}
tr:nth-child(even) td {{ background: #fafcff; }}
.text-right {{ text-align: right; }}
.text-center {{ text-align: center; }}
.chart-wrap {{
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    padding: 20px;
    margin-bottom: 16px;
}}
.chart-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.chart-row .chart-wrap {{ flex: 1; min-width: 300px; }}
.pdf-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}}
.pdf-list a {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #eef2f7;
    border-radius: 8px;
    text-decoration: none;
    color: #003d7a;
    font-size: .85rem;
    font-weight: 500;
    transition: background .15s;
}}
.pdf-list a:hover {{ background: #dce3ed; }}
footer {{
    text-align: center;
    font-size: .8rem;
    color: #6f7e95;
    padding: 24px 0;
    border-top: 1px solid #dce3ed;
    margin-top: 32px;
}}
footer a {{ color: #003d7a; }}
</style>
</head>
<body>
<div class="container">
<header>
    <h1>Indicadores Previsionales 2026</h1>
    <p>Actualizado: {last_update} · Fuentes: <a href="https://www.previred.com/indicadores-previsionales/" target="_blank" style="color:#fff;text-decoration:underline">Previred</a> · <a href="https://www.sii.cl/valores_y_fechas/utm/utm2026.htm" target="_blank" style="color:#fff;text-decoration:underline">SII</a></p>
</header>
<div class="grid" id="cards"></div>
<div class="section">
    <h2>Tabla General — Período Vigente</h2>
    <div class="table-wrap">
        <table><thead><tr><th>Indicador</th><th class="text-right">Valor</th></tr></thead><tbody id="tabla-general"></tbody></table>
    </div>
</div>
<div class="section">
    <h2>Evolución UTM / UTA 2026</h2>
    <div class="chart-row">
        <div class="chart-wrap"><canvas id="chartUtm"></canvas></div>
        <div class="chart-wrap"><canvas id="chartIpc"></canvas></div>
    </div>
</div>
<div class="section" id="section-afp">
    <h2>Tasas de Cotización AFP</h2>
    <div class="table-wrap"><table><thead><tr><th>AFP</th><th class="text-right">Trabajador</th><th class="text-right">Empleador</th><th class="text-right">Total Dependiente</th><th class="text-right">Total Independiente</th></tr></thead><tbody id="tabla-afp"></tbody></table></div>
</div>
<div class="section" id="section-af">
    <h2>Asignación Familiar</h2>
    <div class="table-wrap"><table><thead><tr><th>Tramo</th><th class="text-right">Monto</th><th>Requisito de Renta</th></tr></thead><tbody id="tabla-af"></tbody></table></div>
</div>
<div class="section" id="section-sc">
    <h2>Seguro de Cesantía (AFC)</h2>
    <div class="table-wrap"><table><thead><tr><th>Contrato</th><th class="text-right">Empleador</th><th class="text-right">Trabajador</th></tr></thead><tbody id="tabla-sc"></tbody></table></div>
</div>
<div class="section" id="section-tp">
    <h2>Trabajos Pesados</h2>
    <div class="table-wrap"><table><thead><tr><th>Tipo</th><th class="text-right">%</th><th class="text-right">Empleador</th><th class="text-right">Trabajador</th></tr></thead><tbody id="tabla-tp"></tbody></table></div>
</div>
<div class="section" id="section-pdfs">
    <h2>PDFs Mensuales</h2>
    <div class="pdf-list" id="pdf-list"></div>
</div>
<footer>
    Datos obtenidos de <a href="https://www.previred.com/indicadores-previsionales/" target="_blank">Previred</a> y <a href="https://www.sii.cl/valores_y_fechas/utm/utm2026.htm" target="_blank">SII</a> · Actualizado: {last_update}<br>
    Generado automáticamente · <a href="https://github.com/cursosbackend/scraper-previred" target="_blank">GitHub</a>
</footer>
</div>
<script>
const INDICADORES = {indicadores_json};
const UTM = {utm_json};
const LATEST = {json.dumps(latest, ensure_ascii=False)};
const PDFS = {json.dumps([f.replace('.pdf','') for f in (os.listdir(os.path.join('data','pdfs')) if os.path.isdir(os.path.join('data','pdfs')) else [])], ensure_ascii=False)};

function fmt(n) {{
    if (n === null || n === undefined || n === '') return '—';
    if (typeof n === 'number') return '$ ' + n.toLocaleString('es-CL', {{minimumFractionDigits:0,maximumFractionDigits:2}});
    return n;
}}

function fmtPct(n) {{
    if (n === null || n === undefined || n === '') return '—';
    if (typeof n === 'number') return n.toFixed(2) + '%';
    return n;
}}

// Cards
const cards = [
    ['UF Actual', fmt(LATEST.uf_valor_actual), LATEST.uf_fecha_actual || ''],
    ['UTM Vigente', fmt(LATEST.utm_valor), LATEST.utm_mes || ''],
    ['Renta Mínima', fmt(LATEST.renta_minima_dependientes), 'Trab. Dependientes'],
    ['Tope AFP (90 UF)', fmt(LATEST.renta_tope_afp), ''],
    ['Tope IPS (60 UF)', fmt(LATEST.renta_tope_ips), ''],
    ['SIS', fmtPct(LATEST.sis_tasa), 'Seg. Invalidez y Sobrev.'],
    ['APV Tope Mensual', fmt(LATEST.apv_tope_mensual), '50 UF'],
    ['APV Tope Anual', fmt(LATEST.apv_tope_anual), '600 UF'],
];
document.getElementById('cards').innerHTML = cards.map(c =>
    `<div class="card"><div class="label">${{c[0]}}</div><div class="value">${{c[1]}}</div>${{c[2] ? `<div class="sub">${{c[2]}}</div>` : ''}}</div>`
).join('');

// Tabla general
const generalFields = [
    ['uf_fecha_actual', 'UF — Fecha'], ['uf_valor_actual', 'UF — Valor'],
    ['uf_fecha_anterior', 'UF — Fecha Anterior'], ['uf_valor_anterior', 'UF — Valor Anterior'],
    ['renta_tope_afp', 'Renta Tope AFP (90 UF)'], ['renta_tope_ips', 'Renta Tope IPS (60 UF)'],
    ['renta_tope_seguro_cesantia', 'Renta Tope Seguro Cesantía (135,2 UF)'],
    ['apv_tope_mensual', 'APV Tope Mensual (50 UF)'], ['apv_tope_anual', 'APV Tope Anual (600 UF)'],
    ['deposito_convenido_tope_anual', 'Depósito Convenido Tope Anual (900 UF)'],
    ['renta_minima_dependientes', 'Renta Mínima — Dependientes'],
    ['renta_minima_menores_mayores', 'Renta Mínima — <18 y >65 años'],
    ['renta_minima_casa_particular', 'Renta Mínima — Casa Particular'],
    ['renta_minima_no_remuneracional', 'Renta Mínima — No Remuneracional'],
    ['seguro_social', 'Seguro Social'], ['sis_tasa', 'SIS'],
    ['salud_ccaf', 'Salud — CCAF'], ['salud_fonasa', 'Salud — FONASA'],
];
document.getElementById('tabla-general').innerHTML = generalFields.map(([k, label]) =>
    `<tr><td>${{label}}</td><td class="text-right">${{fmt(LATEST[k])}}</td></tr>`
).join('');

// AFP
if (LATEST.afp_tasas) {{
    const afp = typeof LATEST.afp_tasas === 'string' ? JSON.parse(LATEST.afp_tasas) : LATEST.afp_tasas;
    if (Array.isArray(afp)) {{
        document.getElementById('tabla-afp').innerHTML = afp.map(a =>
            `<tr><td>${{a.nombre || '—'}}</td><td class="text-right">${{fmtPct(a.trabajador)}}</td><td class="text-right">${{fmtPct(a.empleador)}}</td><td class="text-right">${{fmtPct(a.total_dependiente)}}</td><td class="text-right">${{fmtPct(a.total_independiente)}}</td></tr>`
        ).join('');
    }}
}}

// Asignación Familiar
if (LATEST.asignacion_familiar) {{
    const af = typeof LATEST.asignacion_familiar === 'string' ? JSON.parse(LATEST.asignacion_familiar) : LATEST.asignacion_familiar;
    if (Array.isArray(af)) {{
        document.getElementById('tabla-af').innerHTML = af.map(a =>
            `<tr><td>${{a.tramo || '—'}}</td><td class="text-right">${{fmt(a.monto)}}</td><td>${{a.requisito_renta || '—'}}</td></tr>`
        ).join('');
    }}
}}

// Seguro Cesantía
if (LATEST.seguro_cesantia) {{
    const sc = typeof LATEST.seguro_cesantia === 'string' ? JSON.parse(LATEST.seguro_cesantia) : LATEST.seguro_cesantia;
    if (Array.isArray(sc)) {{
        document.getElementById('tabla-sc').innerHTML = sc.map(s =>
            `<tr><td>${{s.contrato || '—'}}</td><td class="text-right">${{s.empleador || '—'}}</td><td class="text-right">${{s.trabajador || '—'}}</td></tr>`
        ).join('');
    }}
}}

// Trabajos Pesados
if (LATEST.trabajos_pesados) {{
    const tp = typeof LATEST.trabajos_pesados === 'string' ? JSON.parse(LATEST.trabajos_pesados) : LATEST.trabajos_pesados;
    if (Array.isArray(tp)) {{
        document.getElementById('tabla-tp').innerHTML = tp.map(t =>
            `<tr><td>${{t.tipo || '—'}}</td><td class="text-right">${{t.porcentaje || '—'}}</td><td class="text-right">${{t.empleador || '—'}}</td><td class="text-right">${{t.trabajador || '—'}}</td></tr>`
        ).join('');
    }}
}}

// PDFs
if (PDFS.length > 0) {{
    document.getElementById('pdf-list').innerHTML = PDFS.map(p =>
        `<a href="../data/pdfs/${{p}}.pdf" target="_blank">📄 ${{p.replace('Indicadores-Previsionales-Previred-','').replace('-',' ')}}</a>`
    ).join('');
}} else {{
    document.getElementById('section-pdfs').style.display = 'none';
}}

// Charts
if (UTM && UTM.length > 0) {{
    const meses = UTM.map(d => d.mes);
    const valores = UTM.map(d => {{
        const v = parseFloat(String(d.utm || '0').replace(/[$.\\s]/g,'').replace(',','.'));
        return isNaN(v) ? 0 : v;
    }});
    const uvas = UTM.map(d => {{
        const v = parseFloat(String(d.uta || '0').replace(/[$.\\s]/g,'').replace(',','.'));
        return isNaN(v) ? 0 : v;
    }});
    const ipcs = UTM.map(d => {{
        const v = parseFloat(String(d.ipc || '0').replace(',','.'));
        return isNaN(v) ? null : v;
    }});

    new Chart(document.getElementById('chartUtm'), {{
        type: 'line',
        data: {{
            labels: meses,
            datasets: [
                {{ label: 'UTM ($)', data: valores, borderColor: '#003d7a', backgroundColor: 'rgba(0,61,122,.1)', fill: true, tension: .3 }},
                {{ label: 'UTA ($)', data: uvas, borderColor: '#c0392b', backgroundColor: 'rgba(192,57,43,.1)', fill: true, tension: .3, yAxisID: 'y1' }},
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            interaction: {{ mode: 'index', intersect: false }},
            plugins: {{ legend: {{ position: 'top' }} }},
            scales: {{
                y: {{ beginAtZero: false, ticks: {{ callback: v => '$' + v.toLocaleString('es-CL') }} }},
                y1: {{ position: 'right', beginAtZero: false, grid: {{ drawOnChartArea: false }}, ticks: {{ callback: v => '$' + v.toLocaleString('es-CL') }} }},
            }}
        }}
    }});

    if (ipcs.some(v => v !== null)) {{
        new Chart(document.getElementById('chartIpc'), {{
            type: 'bar',
            data: {{
                labels: meses,
                datasets: [{{
                    label: 'IPC (puntos)',
                    data: ipcs,
                    backgroundColor: 'rgba(0,61,122,.65)',
                    borderColor: '#003d7a',
                    borderWidth: 1,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
    }} else {{
        document.getElementById('chartIpc').parentElement.innerHTML = '<p style="padding:20px;text-align:center;color:#6f7e95">Datos IPC aún no disponibles</p>';
    }}
}} else {{
    document.querySelector('.chart-row').innerHTML = '<p style="padding:20px;text-align:center;color:#6f7e95">Datos UTM aún no disponibles. Ejecute el scraper primero.</p>';
}}
</script>
</body>
</html>"""
    return html


def main():
    os.makedirs("docs", exist_ok=True)
    indicadores, utm, metas = load_data()
    html = build_html(indicadores, utm, metas)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Dashboard] HTML generado en {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
