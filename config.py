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
    # 'Creado por': 'Ejecutivo CxP'
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
"""GUI"""

# tabs en las que se divide la app
TAB_NAMES = ['Generar conciliación', 'Dashboard', 'Análisis conciliación previa']