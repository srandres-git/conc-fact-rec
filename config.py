import numpy as np

"""CONCILIACIÓN"""
# columnas numéricas de fact_sat
NUM_COLS_FACT_SAT = [
    "SubTotal",
    "Base IVA 16",
    "Base IVA 8",
    "Base IVA 0",
    "Base IVA Exento",
    "Base IEPS",
    "Descuento",
    "IVA",
    "IEPS",
    "Impto. Loc. Tras.",
    "Total Trasladados",
    "IVA Retenido",
    "ISR Retenido",
    "Impto. Loc. Ret.",
    "Total Retenciones",
    "Total",
    "Total Original XML",
    "Tipo Cambio",
    "Tipo Cambio Usuario",
]
DATE_COLS_FACT_SAT = [
    "Fecha Cancelación",
    "Emisión",
    "Fecha Sustitución",
    "Timbrado",
    "Hora Timbrado",
]
# columnas numéricas de fact_sap
NUM_COLS_FACT_SAP = [
    'Importe bruto',
    'Retención de IVA',
    'Retención de ISR',
    'Importe de la factura',
    'Importe compensado',
    'Saldo',
    'Días de vencimiento',
    'No vencido',
    '1-30 días',
    '31-60 días',
    '61-90 días',
    'Más de 90 días',
]

DATE_COLS_FACT_SAP = [
    'Fecha de factura',
    'Fecha de compensación',
    'Fecha de recibo',
    'Fecha de vencimiento',
]
# Columnas de fecha de Box
DATE_COLS_BOX = [
    'Fecha_Modificacion',
]
# columnas numéricas CP
NUM_COLS_CP = [
        'ImpSaldoAnt',
       'ImpPagado', 'ImpSaldoInsoluto', 'Base IVA Exento Traslado',
       'IVA Exento Traslado', 'Base IVA 8% Traslado', 'IVA 8% Traslado',
       'Base IVA 4% Retención', 'IVA 4% Retención', 'Base IVA 16% Traslado',
       'IVA 16% Traslado', 'Base IVA 16% Retención', 'IVA 16% Retención',
       'Base IVA 10.67% Retención', 'IVA 10.67% Retención',
       'Base IVA 0% Traslado', 'IVA 0% Traslado', 'Base IVA 0% Retención',
       'IVA 0% Retención', 'Base ISR 10% Retención', 'ISR 10% Retención',
       'Base ISR 1.25% Retención', 'ISR 1.25% Retención',
       'Base IEPS 3% Traslado', 'IEPS 3% Traslado',
       'TipoCambioDR', 'Monto', 'TipoCambioP'
]
DATE_COLS_CP = [
    'Fecha', 'FechaPago',
]

# Renombramiento de columnas de los reportes base
RENAME_COLS_SAP = {
    'UUID Corregido': 'UUID SAP',
    'Estado de factura': 'Estatus SAP',
    'Referencia externa': 'Ref. externa SAP',
    'Importe de la factura': 'Total SAP XML',
    'Importe compensado': 'Pagado SAP XML',
    'Fecha de compensación': 'Fecha de pago',
    # 'Creado por': 'Ejecutivo CxP'
}

# Conlumnas donde se busca el número de servicio
COLS_SERVICE = ['Ref. externa SAP','Ruta Box', 'Conceptos Descripción']

# columnas en el orden final de la conciliación
COLS_CONC = [
    'Estatus', # verde
    'Estatus SAP', 'Estatus CP', 'Comentario', 'Servicio', 'Estatus Box', 'Ejecutivo CxP', # amarillo
    'Estatus Sustitución', 'Estatus para Cancelación', 'Estatus Cancelación', 'Fecha Cancelación', 'Ver.', 'CFDI Relacionado', 'Tipo Relación CFDI', # verde
    'Tipo Relación CFDI Descripción', 'Tipo', 'UUID', 'UUID Sustitución', 'Serie', 'Folio', # verde
    'Ref. externa SAP', 'Tipo de servicio', # amarillo
    'Emisión', # verde
    'Mes', # azul
    'Fecha Sustitución', 'Uso CFDI', # verde
    'ID Proveedor SAP', # amarillo
    'Emisor RFC', 'Emisor Nombre', 'Emisor Régimen Fiscal', 'Emisor Régimen Fiscal Descripción', 'Conceptos Descripción', 'Conceptos ClaveProdServ SAT', # verde
    'Conceptos ClaveProdServ SAT Descripción', 
    'Fecha de pago', # azul
    'Mes de pago', # azul
    'Pagado SAP XML', # amarillo
    'SubTotal', 'Total SAT MXN', # verde
    'Total SAP MXN', 'Dif. Total MXN', # amarillo
    'Total SAT XML', # verde
    'Total SAP XML', 'Dif. Total XML', # amarillo
    'Tipo Cambio', 'Moneda', 'Forma Pago', 'Método Pago', # verde
]

# columnas esperadas en cada reporte inicial
EXPECTED_COLS = {
    'fact_sat': NUM_COLS_FACT_SAT+DATE_COLS_FACT_SAT+[
        'UUID','Moneda','CFDI Relacionado', 'UUID Sustitución', 'Estatus'
    ],
    'fact_sap': NUM_COLS_FACT_SAP+DATE_COLS_FACT_SAP+[
        'UUID Corregido', 'Estado de factura', 'Referencia externa','Creado por'
    ],
    'box': [
        'UUID', 'Estatus', 'Ruta_Archivo', 'Fecha_Modificacion'
    ],
    'cp': NUM_COLS_CP+DATE_COLS_CP+[
        'UUIDRel', 'Estatus',
    ],
}


# ejecutivos
EJECUTIVO_SAP_MAP = {
    'MANUEL QUIROZ / CARMEN MORENO':'CARMEN MORENO / MANUEL QUIROZ',
    'MANUEL QUIROZ (USD) / CARMEN MORENO (MXN)':'CARMEN MORENO / MANUEL QUIROZ',
    'ARMEN MORENO': 'CARMEN MORENO',
    'MARIA  DEL CARMEN': 'CARMEN MORENO',
    'CARMEN ORENO': 'CARMEN MORENO',
    'PAOLA AGUIRRE/ ALFREDO ZAMUDIO': 'PAOLA AGUIRRE / ALFREDO ZAMUDIO',
    'CARMEN MORENO\n': 'CARMEN MORENO',
    'PAGUIRRE': 'PAOLA AGUIRRE',
    'CMORENO': 'CARMEN MORENO',
    'MQUIROZ': 'MANUEL QUIROZ',
    'EVERGARA': 'ENRIQUE VERGARA',
    'AZAMUDIO': 'ALFREDO ZAMUDIO',
    '_SUPPINV': np.nan,
    'CTELLEZ2': np.nan,
    '': np.nan
}

# Comentarios según el estatus en SAT, SAP y el CP
# (Estatus SAT| Estatus SAP| Estatus CP): Comentario
COMENTARIOS = {
    ('Vigente', 'Cancelada', 'Cancelado'): 'Revisar // Vigente SAT - Cancelada SAP',
    ('Vigente', 'Contabilizada', 'Cancelado'): 'OK // Vigente SAT - Contabilizada SAP',
    ('Vigente', 'No está SAP', 'Cancelado'): 'Revisar // Vigente SAT - No está en SAP',
    ('Vigente', 'Pagado', 'Cancelado'): 'Revisar // Vigente SAT - Pagado SAP - Tiene CP cancelado',
    ('Vigente', 'Parcialmente pagado', 'Cancelado'): 'Revisar // Vigente SAT - Parcialmente pagado SAP - Tiene CP cancelado',
    ('Vigente', 'Cancelada', 'Sin CP'): 'Revisar // Vigente SAT - Cancelada SAP',
    ('Vigente', 'Contabilizada', 'Sin CP'): 'OK // Vigente SAT - Contabilizada SAP',
    ('Vigente', 'No está SAP', 'Sin CP'): 'Revisar // Vigente SAT - No está en SAP',
    ('Vigente', 'Pagado', 'Sin CP'): 'Revisar // Vigente SAT - Pagado SAP - Sin CP',
    ('Vigente', 'Parcialmente pagado', 'Sin CP'): 'Revisar // Vigente SAT - Parcialmente pagado SAP - Sin CP',
    ('Vigente', 'Cancelada', 'Vigente'): 'Revisar // Vigente SAT - Cancelada SAP',
    ('Vigente', 'Contabilizada', 'Vigente'): 'Revisar // Vigente SAT - Contabilizada SAP - CP vigente',
    ('Vigente', 'No está SAP', 'Vigente'): 'Revisar // Vigente SAT - No está en SAP',
    ('Vigente', 'Pagado', 'Vigente'): 'OK // Vigente SAT - Pagado  SAP - CP vigente',
    ('Vigente', 'Parcialmente pagado', 'Vigente'): 'OK // Vigente SAT - Parcialmente pagado  SAP - CP vigente',
    ('Cancelado', 'Cancelada', 'Cancelado'): 'OK // Cancelado SAT - Cancelada SAP - CP cancelado',
    ('Cancelado', 'Contabilizada', 'Cancelado'): 'Revisar // Cancelado SAT - Contabilizado SAP',
    ('Cancelado', 'No está SAP', 'Cancelado'): 'OK // Cancelado SAT - No está en SAP',
    ('Cancelado', 'Pagado', 'Cancelado'): 'Revisar // Cancelado SAT - Pagado SAP',
    ('Cancelado', 'Parcialmente pagado', 'Cancelado'): 'Revisar // Cancelado SAT - Parcialmente pagado SAP',
    ('Cancelado', 'Cancelada', 'Sin CP'): 'OK // Cancelado SAT - Cancelada SAP',
    ('Cancelado', 'Contabilizada', 'Sin CP'): 'Revisar // Cancelado SAT - Contabilizado SAP',
    ('Cancelado', 'No está SAP', 'Sin CP'): 'OK // Cancelado SAT - No está en SAP',
    ('Cancelado', 'Pagado', 'Sin CP'): 'Revisar // Cancelado SAT - Pagado SAP',
    ('Cancelado', 'Parcialmente pagado', 'Sin CP'): 'Revisar // Cancelado SAT - Parcialmente pagado SAP',
    ('Cancelado', 'Cancelada', 'Vigente'): 'Revisar // Cancelado SAT - Cancelada SAP - CP vigente',
    ('Cancelado', 'Contabilizada', 'Vigente'): 'Revisar // Cancelado SAT - Contabilizada SAP - CP vigente',
    ('Cancelado', 'No está SAP', 'Vigente'): 'Revisar // Cancelado SAT - No está en SAP - CP vigente',
    ('Cancelado', 'Pagado', 'Vigente'): 'Revisar // Cancelado SAT - Pagado SAP - CP vigente',
    ('Cancelado', 'Parcialmente pagado', 'Vigente'): 'Revisar // Cancelado SAT - Parcialmente pagado SAP - CP vigente',

}

# los siguientes estatus no aplican para PUE:
ESTATUS_NA_PUE = ['Revisar // Vigente SAT - Pagado SAP - Tiene CP cancelado', 'Revisar // Vigente SAT - Parcialmente pagado SAP - Tiene CP cancelado', \
          'Revisar // Vigente SAT - Pagado SAP - Sin CP', 'Revisar // Vigente SAT - Parcialmente pagado SAP - Sin CP']
# los tipos de servicio que corresponden a servicio de transporte
SERVS_TRANSPORTE = ['Terrestre', 'AE', 'AI', 'ME', 'MI']

# Mapeo de meses inglés a español
MONTH_MAP_ENG_ESP = {
    'Jan': 'Enero',
    'Feb': 'Febrero',
    'Mar': 'Marzo',
    'Apr': 'Abril',
    'May': 'Mayo',
    'Jun': 'Junio',
    'Jul': 'Julio',
    'Aug': 'Agosto',
    'Sep': 'Septiembre',
    'Oct': 'Octubre',
    'Nov': 'Noviembre',
    'Dec': 'Diciembre',
}

"""GUI"""

# tabs en las que se divide la app
TAB_NAMES = ['Generar conciliación', 'Dashboard', ]

# valores por default de los filtros en el dashboard

FILTERS = {
    'estatus':{'Tipo de servicio':SERVS_TRANSPORTE, 'Mes':None, 'Estatus Box':None, 'Ejecutivo CxP':None, },
    'no_sap_mes': {'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Estatus Box':None, 'Ejecutivo CxP':None,},
    'no_sap_mes_box': {'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Ejecutivo CxP':None,},
    'no_sap_top':{'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Mes':None, 'Estatus Box':None, 'Ejecutivo CxP':None,}
}
MONTH_ORDER = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# mapeo de funciones de depuración para cada reporte
CLEANING_FUNCTIONS = {
    'fact_sat': 'depurar_sat',
    'fact_sap': 'depurar_sap',
    'box': 'depurar_box',
    'cp': 'depurar_cp',
}