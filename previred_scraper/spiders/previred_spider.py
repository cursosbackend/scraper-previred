import re
from datetime import datetime

import scrapy

from previred_scraper.items import IndicadoresItem, PdfItem


MONTH_MAP = {
    "enero": "Enero", "febrero": "Febrero", "marzo": "Marzo",
    "abril": "Abril", "mayo": "Mayo", "junio": "Junio",
    "julio": "Julio", "agosto": "Agosto", "septiembre": "Septiembre",
    "octubre": "Octubre", "noviembre": "Noviembre", "diciembre": "Diciembre",
}


def clean(val):
    if val is None:
        return None
    val = val.strip().replace("\xa0", " ")
    return val if val else None


def parse_currency(text):
    if not text:
        return None
    text = text.strip().replace("$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(text)
    except ValueError:
        return clean(text)


def parse_percent(text):
    if not text:
        return None
    text = text.strip().replace("%", "").replace(",", ".").strip()
    try:
        return float(text)
    except ValueError:
        return clean(text)


class PreviredSpider(scrapy.Spider):
    name = "previred"
    start_urls = ["https://www.previred.com/indicadores-previsionales/"]

    def parse(self, response):
        item = IndicadoresItem()
        item["fecha_extraccion"] = datetime.now().isoformat()

        # --- Periodo ---
        intro_text = " ".join(response.xpath("//table//tr[1]/td[1]//text()").getall())
        m = re.search(r"(\w+)\s+(\d{4})", intro_text)
        if m:
            item["periodo_cotizacion"] = f"{MONTH_MAP.get(m.group(1).lower(), m.group(1))} {m.group(2)}"
        m2 = re.search(r"remuneraciones\s+(\w+)\s+(\d{4})", intro_text, re.IGNORECASE)
        if m2:
            item["periodo_remuneracion"] = f"{MONTH_MAP.get(m2.group(1).lower(), m2.group(1))} {m2.group(2)}"

        # --- Helper: find table by header text ---
        def find_table(heading_text):
            xp = (
                f"//table[.//td[contains(@class, 'encabezado_tabla_ind') "
                f"and contains(normalize-space(.), '{heading_text}')]]"
            )
            tables = response.xpath(xp)
            if tables:
                return tables[0]
            return None

        def table_rows(table):
            return table.xpath(".//tr")

        def row_tds(tr):
            return tr.xpath(".//td")

        # --- UF ---
        uf_table = find_table("VALOR UF")
        if uf_table is not None:
            rows = uf_table.xpath(".//tr[position()>1 and not(contains(td, 'encabezado'))]")
            for tr in rows:
                tds = tr.xpath(".//td")
                if len(tds) >= 2:
                    label = clean("".join(tds[0].xpath(".//text()").getall()))
                    value = clean("".join(tds[1].xpath(".//text()").getall()))
                    value_p = parse_currency(value)
                    if "actual" in label.lower() or "mayo" in label.lower():
                        item["uf_valor_actual"] = value_p
                        date_m = re.search(r"(\d+)\s+de\s+(\w+)", label)
                        if date_m:
                            item["uf_fecha_actual"] = label.strip()
                    else:
                        item["uf_valor_anterior"] = value_p
                        date_m = re.search(r"(\d+)\s+de\s+(\w+)", label)
                        if date_m:
                            item["uf_fecha_anterior"] = label.strip()

        # --- Rentas Topes ---
        topes_table = find_table("RENTAS TOPES IMPONIBLES")
        if topes_table is not None:
            for tr in topes_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 2:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall())) or ""
                value = clean("".join(tds[1].xpath(".//text()").getall()))
                if "afp" in label.lower():
                    item["renta_tope_afp"] = parse_currency(value)
                elif "ips" in label.lower() or "inp" in label.lower():
                    item["renta_tope_ips"] = parse_currency(value)
                elif "cesant" in label.lower():
                    item["renta_tope_seguro_cesantia"] = parse_currency(value)

        # --- AFP Tasas ---
        afp_table = find_table("TASA COTIZACIÓN AFP")
        if afp_table is not None:
            afp_data = []
            for tr in afp_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 5:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall()))
                if not label or label in ("AFP", "Capital"):
                    continue
                if any(h in (label or "").lower() for h in ("dependientes", "independientes", "cargo del", "total a")):
                    continue
                afp_data.append({
                    "nombre": label,
                    "trabajador": clean("".join(tds[1].xpath(".//text()").getall())),
                    "empleador": clean("".join(tds[2].xpath(".//text()").getall())),
                    "total_dependiente": clean("".join(tds[3].xpath(".//text()").getall())),
                    "total_independiente": clean("".join(tds[4].xpath(".//text()").getall())),
                })
            item["afp_tasas"] = afp_data

        # --- Seguro Cesantía ---
        sc_table = find_table("SEGURO DE CESANTÍA")
        if sc_table is not None:
            sc_data = []
            for tr in sc_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 3:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall()))
                if not label or label in ("CONTRATO", "FINANCIAMIENTO", "EMPLEADOR", "TRABAJADOR"):
                    continue
                sc_data.append({
                    "contrato": label,
                    "empleador": clean("".join(tds[1].xpath(".//text()").getall())),
                    "trabajador": clean("".join(tds[2].xpath(".//text()").getall())),
                })
            item["seguro_cesantia"] = sc_data

        # --- APV ---
        apv_table = find_table("AHORRO PREVISIONAL VOLUNTARIO")
        if apv_table is not None:
            for tr in apv_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 2:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall())) or ""
                value = clean("".join(tds[1].xpath(".//text()").getall()))
                if "mensual" in label.lower():
                    item["apv_tope_mensual"] = parse_currency(value)
                elif "anual" in label.lower():
                    item["apv_tope_anual"] = parse_currency(value)

        # --- Depósito Convenido ---
        dc_table = find_table("DEPÓSITO CONVENIDO")
        if dc_table is not None:
            for tr in dc_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 2:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall())) or ""
                value = clean("".join(tds[1].xpath(".//text()").getall()))
                if "anual" in label.lower():
                    item["deposito_convenido_tope_anual"] = parse_currency(value)

        # --- Rentas Mínimas ---
        rm_table = find_table("RENTAS MÍNIMAS IMPONIBLES")
        if rm_table is not None:
            for tr in rm_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 2:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall())) or ""
                value = clean("".join(tds[1].xpath(".//text()").getall()))
                if "dependientes" in label.lower() and "independientes" in label.lower():
                    item["renta_minima_dependientes"] = parse_currency(value)
                elif "menores" in label.lower():
                    item["renta_minima_menores_mayores"] = parse_currency(value)
                elif "casa particular" in label.lower():
                    item["renta_minima_casa_particular"] = parse_currency(value)
                elif "no remuneracionales" in label.lower():
                    item["renta_minima_no_remuneracional"] = parse_currency(value)

        # --- Seguro Social ---
        ss_table = find_table("SEGURO SOCIAL")
        if ss_table is not None:
            for tr in ss_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 2:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall())) or ""
                value = clean("".join(tds[1].xpath(".//text()").getall()))
                if "expectativa" in label.lower():
                    item["seguro_social"] = parse_percent(value)

        # --- SIS ---
        sis_table = find_table("SEGURO DE INVALIDEZ")
        if sis_table is not None:
            for tr in sis_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 2:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall())) or ""
                value = clean("".join(tds[1].xpath(".//text()").getall()))
                if "tasa" in label.lower():
                    item["sis_tasa"] = parse_percent(value)

        # --- Salud ---
        salud_table = find_table("DISTRIBUCIÓN DEL 7% SALUD")
        if salud_table is not None:
            for tr in salud_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 2:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall())) or ""
                value = clean("".join(tds[1].xpath(".//text()").getall()))
                if "ccaf" in label.lower():
                    item["salud_ccaf"] = clean(value)
                elif "fonasa" in label.lower():
                    item["salud_fonasa"] = clean(value)

        # --- Trabajos Pesados ---
        tp_table = find_table("TRABAJOS PESADOS")
        if tp_table is not None:
            tp_data = []
            for tr in tp_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 4:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall()))
                if not label or label in ("CALIFICACIÓN", "PUESTO DE TRABAJO", "FINANCIAMIENTO"):
                    continue
                tp_data.append({
                    "tipo": label,
                    "porcentaje": clean("".join(tds[1].xpath(".//text()").getall())),
                    "empleador": clean("".join(tds[2].xpath(".//text()").getall())),
                    "trabajador": clean("".join(tds[3].xpath(".//text()").getall())),
                })
            item["trabajos_pesados"] = tp_data

        # --- Asignación Familiar ---
        af_table = find_table("ASIGNACIÓN FAMILIAR")
        if af_table is not None:
            af_data = []
            for tr in af_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 3:
                    continue
                label = clean("".join(tds[0].xpath(".//text()").getall()))
                if not label or label in ("TRAMO", "MONTO"):
                    continue
                af_data.append({
                    "tramo": label,
                    "monto": clean("".join(tds[1].xpath(".//text()").getall())),
                    "requisito_renta": clean("".join(tds[2].xpath(".//text()").getall())),
                })
            item["asignacion_familiar"] = af_data

        # --- UTM/UTA from Previred (fallback, main source is SII) ---
        utm_table = find_table("UTM")
        if utm_table is None:
            utm_table = find_table("VALOR")
        if utm_table is not None:
            for tr in utm_table.xpath(".//tr"):
                tds = tr.xpath(".//td")
                if len(tds) < 3:
                    continue
                mes_label = clean("".join(tds[0].xpath(".//text()").getall()))
                utm_val = clean("".join(tds[1].xpath(".//text()").getall()))
                uta_val = clean("".join(tds[2].xpath(".//text()").getall()))
                if mes_label and utm_val and mes_label.lower() not in ("valor", "utm"):
                    item["utm_mes"] = mes_label
                    item["utm_valor"] = parse_currency(utm_val)
                    item["uta_valor"] = parse_currency(uta_val)
                    break

        yield item

        # --- PDFs ---
        pdf_section = response.xpath(
            "//div[contains(@class, 'accordion__header') "
            "and contains(normalize-space(.), '2026')]/following-sibling::div[1]"
        )
        if pdf_section:
            for link in pdf_section.xpath(".//a[contains(@href, '.pdf')]"):
                url = link.xpath("@href").get()
                text = clean("".join(link.xpath(".//text()").getall()))
                if url:
                    url = response.urljoin(url)
                    yield PdfItem(
                        mes=text,
                        file_urls=[url],
                        file_name=url.split("/")[-1],
                    )
