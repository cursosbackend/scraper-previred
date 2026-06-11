import os
from datetime import datetime

import pandas as pd
from scrapy.pipelines.files import FilesPipeline


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
EXCEL_PATH = os.path.join(DATA_DIR, "indicadores_2026.xlsx")

MONTH_ORDER = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

MES_NUM = {m: f"{i+1:02d}" for i, m in enumerate(MONTH_ORDER)}

TOTAL_SPIDERS = 2
_spider_close_count = 0


class DataCollector:
    indicadores = {}
    utm_rows = []
    pdf_links = []


def save_excel():
    os.makedirs(DATA_DIR, exist_ok=True)
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        if DataCollector.indicadores:
            df = pd.DataFrame.from_dict(DataCollector.indicadores, orient="index")
            df.index.name = "periodo_remuneracion"
            df.to_excel(writer, sheet_name="Indicadores")
        else:
            pd.DataFrame({"info": ["Sin datos"]}).to_excel(writer, sheet_name="Indicadores")

        if DataCollector.utm_rows:
            df_utm = pd.DataFrame(DataCollector.utm_rows)
            df_utm["mes_num"] = df_utm["mes"].map(MES_NUM)
            df_utm = df_utm.sort_values("mes_num").drop(columns=["mes_num"])
            df_utm.to_excel(writer, sheet_name="UTM_UTA", index=False)

        meta = pd.DataFrame({
            "clave": ["ultima_actualizacion", "fuente_previred", "fuente_sii"],
            "valor": [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "https://www.previred.com/indicadores-previsionales/",
                "https://www.sii.cl/valores_y_fechas/utm/utm2026.htm",
            ],
        })
        meta.to_excel(writer, sheet_name="Metadatos", index=False)
    print(f"[ExcelPipeline] Excel guardado en {EXCEL_PATH}")


class ExcelPipeline:
    def process_item(self, item, spider):
        if spider.name == "previred" and item.get("periodo_remuneracion"):
            periodo = item.get("periodo_remuneracion")
            data = dict(item)
            data.pop("periodo_remuneracion", None)
            DataCollector.indicadores[periodo] = data
        elif spider.name == "sii_utm":
            DataCollector.utm_rows.append(dict(item))
        return item

    def close_spider(self, spider):
        global _spider_close_count
        _spider_close_count += 1
        if _spider_close_count >= TOTAL_SPIDERS:
            save_excel()


class PdfsPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        name = item.get("file_name", request.url.split("/")[-1])
        if not name.endswith(".pdf"):
            name += ".pdf"
        return name

    def process_item(self, item, spider):
        if not item.get("file_urls"):
            return item
        return super().process_item(item, spider)

    def item_completed(self, results, item, info):
        if results:
            ok, result = results[0]
            if ok:
                item["file_path"] = result["path"]
        return item
