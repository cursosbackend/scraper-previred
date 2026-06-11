import scrapy


class IndicadoresItem(scrapy.Item):
    periodo_cotizacion = scrapy.Field()
    periodo_remuneracion = scrapy.Field()

    uf_fecha_actual = scrapy.Field()
    uf_valor_actual = scrapy.Field()
    uf_fecha_anterior = scrapy.Field()
    uf_valor_anterior = scrapy.Field()

    renta_tope_afp = scrapy.Field()
    renta_tope_ips = scrapy.Field()
    renta_tope_seguro_cesantia = scrapy.Field()

    afp_tasas = scrapy.Field()

    seguro_cesantia = scrapy.Field()

    apv_tope_mensual = scrapy.Field()
    apv_tope_anual = scrapy.Field()

    deposito_convenido_tope_anual = scrapy.Field()

    renta_minima_dependientes = scrapy.Field()
    renta_minima_menores_mayores = scrapy.Field()
    renta_minima_casa_particular = scrapy.Field()
    renta_minima_no_remuneracional = scrapy.Field()

    seguro_social = scrapy.Field()
    sis_tasa = scrapy.Field()

    salud_ccaf = scrapy.Field()
    salud_fonasa = scrapy.Field()

    trabajos_pesados = scrapy.Field()

    asignacion_familiar = scrapy.Field()

    utm_mes = scrapy.Field()
    utm_valor = scrapy.Field()
    uta_valor = scrapy.Field()

    fecha_extraccion = scrapy.Field()


class UTMItem(scrapy.Item):
    mes = scrapy.Field()
    utm = scrapy.Field()
    uta = scrapy.Field()
    ipc = scrapy.Field()
    var_mensual = scrapy.Field()
    var_acumulada = scrapy.Field()
    var_anual = scrapy.Field()


class PdfItem(scrapy.Item):
    mes = scrapy.Field()
    file_urls = scrapy.Field()
    file_name = scrapy.Field()
    file_path = scrapy.Field()
