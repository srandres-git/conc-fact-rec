import io
import pandas as pd
import numpy as np
import streamlit as st
from config import COLS_CONC, COMENTARIOS, ESTATUS_NA_PUE, RENAME_COLS_SAP, EJECUTIVO_SAP_MAP
from export import export_conciliacion_facturas
from utils import assign_service_type, find_service, get_provs

def sat_x_sap(fact_sat: pd.DataFrame, fact_sap: pd.DataFrame)->pd.DataFrame:
    """Cruce de facturas de SAT vs SAP. Ambos reportes iniciales depurados."""

    fact_sat = fact_sat.merge(fact_sap[['UUID Corregido','Estado de factura','Referencia externa','Creado por','Importe de la factura']], left_on='UUID', right_on='UUID Corregido', how='left', suffixes=('', '_sap'))
    fact_sat.rename(columns=RENAME_COLS_SAP, inplace=True)
    fact_sat.replace({'Creado por': EJECUTIVO_SAP_MAP}, inplace=True)

    # los NaN en 'UUID Corregido', 'Estado de factura', 'Referencia externa' se ponen como "No está SAP"
    fact_sat['UUID SAP'] = fact_sat['UUID SAP'].fillna('No está SAP')
    fact_sat['Estatus SAP'] = fact_sat['Estatus SAP'].fillna('No está SAP')
    fact_sat['Ref. externa SAP'] = fact_sat['Ref. externa SAP'].fillna('No está SAP')
    # los NaN en 'Importe de la factura' se ponen como 0
    fact_sat['Total SAP XML'] = fact_sat['Total SAP XML'].fillna(0)
    # calculamos Total SAP MXN
    fact_sat['Total SAP MXN'] = fact_sat['Total SAP XML'] * fact_sat['Tipo Cambio']
    # diferencias entre SAT y SAP, MXN y XML
    fact_sat['Dif. Total MXN'] = (fact_sat['Total SAT MXN'] - fact_sat['Total SAP MXN']).abs()
    fact_sat['Dif. Total XML'] = (fact_sat['Total SAT XML'] - fact_sat['Total SAP XML']).abs()

    return fact_sat



def sat_x_box(fact_sat: pd.DataFrame, box: pd.DataFrame)->pd.DataFrame:
    """Cruce de facturas de SAT vs Box. Ambos reportes iniciales previamente depurados."""
    # extraemos los RFC de las facturas de Box
    rfcs_box = box['Emisor_RFC'].str.upper().str.strip().unique()

    # cruzamos Box con fact_sat
    fact_sat = fact_sat.merge(box[['UUID','Estatus','Ruta_Archivo']], left_on='UUID', right_on='UUID', how='left', suffixes=('', ' Box'))
    fact_sat.rename(columns={'Ruta_Archivo': 'Ruta Box'}, inplace=True)

    # separamos los que están en Box y los que no
    fact_sat_in_box = fact_sat[fact_sat['Estatus Box'].notna()].copy()
    fact_sat_not_in_box = fact_sat[fact_sat['Estatus Box'].isna()].copy()

    # de los que no están en Box, verificamos si el RFC del emisor está en los RFCS de Box
    # si es así, se les pone 'No está Box'; si no, se les pone 'No buscado en Box'
    fact_sat_not_in_box['Estatus Box'] = np.where(
        fact_sat_not_in_box['Emisor RFC'].str.upper().str.strip().isin(rfcs_box),
        'No está Box',
        'No buscado en Box'
    )
    # unimos los dos dataframes
    fact_sat = pd.concat([fact_sat_in_box, fact_sat_not_in_box], ignore_index=True)
    # Aignamos los mismos valores en 'Ruta Box' para los documentos no encontrados en Box
    fact_sat['Ruta Box'] = fact_sat['Ruta Box'].fillna(fact_sat['Estatus Box'])

    return fact_sat

def sat_x_cp(fact_sat: pd.DataFrame, cp: pd.DataFrame)->pd.DataFrame:
    """Cruce de facturas de SAT vs complementos de pago. Ambos reportes iniciales previamente depurados."""
    # hacemos merge con cp para obtener estatus de pagos
    fact_sat = fact_sat.merge(cp[['UUIDRel','Estatus']], left_on='UUID', right_on='UUIDRel', how='left', suffixes=('', ' CP'))
    # rellenamos los NaN en 'Estatus CP' con 'Sin CP'
    fact_sat['Estatus CP'] = fact_sat['Estatus CP'].fillna('Sin CP')

    return fact_sat

def validate_non_empty_initial_reports()->bool:
    """Valida que los reportes iniciales cargados no estén vacíos."""
    for report_name in ['fact_sat', 'fact_sap', 'box', 'cp']:
        df = st.session_state.get(report_name, None)
        if df is None or df.empty:
            st.error(f'El reporte inicial "{report_name}" no ha sido cargado o está vacío. Por favor, carga un archivo válido.', icon="❌")
            return False
    return True

def conciliar(fact_sat: pd.DataFrame, fact_sap: pd.DataFrame, box: pd.DataFrame, cp: pd.DataFrame, output_file=""):
    """Realiza la conciliación de facturas recibidas cruzando los reportes iniciales depurados."""
    if not validate_non_empty_initial_reports():
        return
    for report in ['fact_sat', 'fact_sap', 'box', 'cp']:
        st.write(st.session_state[report])
    # reiniciamos las variables de sesión
    st.session_state['conciliacion'] = None
    st.session_state['output_file'] = None
    st.session_state['dashboard_loaded'] = False
    # Realizamos los cruces de los reportes base
    with st.session_state['conc_container']: # update
        st.info('Cruzando los reportes iniciales...', icon="ℹ️")
    fact_sat = sat_x_sap(fact_sat,fact_sap)
    fact_sat = sat_x_box(fact_sat, box)
    fact_sat = sat_x_cp(fact_sat, cp)

    # asignamos el ID de proveedor
    with st.session_state['conc_container']: # update
        st.info('Asignando ID de proveedor...', icon="ℹ️")
    rfc_list = fact_sat['Emisor RFC'].str.upper().str.strip().unique().tolist()
    with st.session_state['conc_container']: # update
        st.info(f'Buscando datos de {len(rfc_list)} proveedores en SAP...', icon="ℹ️")
    provs = get_provs(rfc_list, bucket_size=40)
    provs.replace({'Ejecutivo CPP SAP': EJECUTIVO_SAP_MAP}, inplace=True)
    fact_sat = fact_sat.merge(provs[['ID Proveedor SAP','RFC Proveedor', 'Ejecutivo CPP SAP']], left_on='Emisor RFC', right_on='RFC Proveedor', how='left', suffixes=('', '_prov'))
    fact_sat['ID Proveedor SAP'] = fact_sat['ID Proveedor SAP'].fillna('No identificado')

    # asignamos comentarios según los estatus
    with st.session_state['conc_container']: # update
        st.info('Asignando comentarios según estatus...', icon="ℹ️")
    fact_sat['Comentario'] = fact_sat.apply(lambda row: COMENTARIOS.get((row['Estatus'], row['Estatus SAP'], row['Estatus CP']), 'Revisar // Caso no contemplado'), axis=1)
    # arreglamos los de método de pago PUE
    fact_sat['Comentario'].where((fact_sat['Método Pago']=='PPD')\
                                |~(fact_sat['Comentario'].isin(ESTATUS_NA_PUE)),\
                                fact_sat['Comentario'].str.replace('Revisar', 'OK')+' (PUE)',
                                inplace=True)
    
    # asignamos el ejecutivo de CxP
    with st.session_state['conc_container']: # update
        st.info('Asignando ejecutivo de CxP...', icon="ℹ️")
    ejecutivos_cxp = pd.DataFrame(st.secrets["ejecutivos_cxp"])
    # inicialmente cruzamos con los datos históricos de la tabla de ejecutivos
    fact_sat = fact_sat.merge(ejecutivos_cxp, left_on=['Emisor RFC', 'Moneda'], right_on=['rfc', 'moneda'], how='left',)
    # Creamos la columna 'Ejecutivo CxP' y la llenamos como sigue:
    # primero con los de la columna 'Creado por' (proveniente de fact_sap)
    # los que queden vacíos, con el valor de la columna 'ejecutivo_cxp' (proveniente de los datos históricos)
    # los que queden vacíos, con la columna 'Ejecutivo CPP SAP' (proveniente de la base de proveedores prov)
    # los que queden vacíos, son asignados 'No identificado'
    fact_sat['Ejecutivo CxP'] = fact_sat['Creado por'] \
        .fillna(fact_sat['ejecutivo_cxp']) \
        .fillna(fact_sat['Ejecutivo CPP SAP']) \
        .fillna('No identificado')
    
    # asignamos el número de servicio
    with st.session_state['conc_container']: # update
        st.info('Asignando número de servicio...', icon="ℹ️")
    fact_sat['Servicio'] = fact_sat.apply(find_service, axis=1)

    # asignamos el tipo de servicio
    with st.session_state['conc_container']: # update
        st.info('Asignando tipo de servicio...', icon="ℹ️")
    fact_sat['Tipo de servicio'] = fact_sat.apply(assign_service_type, axis=1)

    st.session_state['conciliacion'] = fact_sat[COLS_CONC]

    # exportamos el reporte de conciliación
    if output_file=="":
        output_file = io.BytesIO()
    with st.session_state['conc_container']: # update
        st.info('Generando reporte de conciliación...', icon="ℹ️")
    export_conciliacion_facturas(st.session_state['conciliacion'], output_file, COLS_CONC)
    st.session_state['output_file'] = output_file