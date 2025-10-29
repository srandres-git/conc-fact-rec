import streamlit as st
import pandas as pd
from analytics import dtable_estatus, dtable_no_sap_mes, dtable_no_sap_mes_box, dtable_no_sap_top
from utils import multiselect_key, get_multiselect_values
from config import FILTERS
# pestaña del dashboard
st.set_page_config(layout="wide")
st.title("Resumen de conciliación")
# --- Cargar conciliación previa o usar la generada ---
uploaded_file = st.file_uploader(
    'Cargar conciliación previa',
    type='xlsx',
    accept_multiple_files=False,
    key='file_conc'
)

# Si se sube un archivo nuevo, actualizamos el DataFrame en session_state
if uploaded_file is not None:
    st.session_state['conciliacion'] = pd.read_excel(uploaded_file, header=1)
    st.session_state['dashboard_loaded'] = False

# Si ya tenemos una conciliación (cargada o generada)
# Creamos tabs para mostrar las distintas tablas del dashboard
tab_estatus, tab_no_sap_mes, tab_no_sap_mes_box, tab_no_sap_top = st.tabs([
    'Por estatus',
    'Faltantes en SAP por mes',
    'Faltantes en SAP por carpeta Box',
    'Top proveedores faltantes en SAP'
])
filters = {}
with tab_estatus:
    st.header('Resumen por Comentarios de Estatus')
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
        name = 'estatus'
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            filters[name][col] = st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('dtable_'+name, col)
            )            
        # filters = get_multiselect_values('dtable_'+name, FILTERS[name])
        dtable_estatus(st.session_state['conciliacion'], filters=filters[name])
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")
with tab_no_sap_mes:
    st.header('Facturas no encontradas en SAP por Mes')
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
        name = 'no_sap_mes'
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            filters[name][col] = st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('dtable_'+name, col)
            )
        # filters = get_multiselect_values('dtable_'+name, FILTERS[name])
        # dtable_no_sap_mes(st.session_state['conciliacion'], filters=FILTERS['no_sap_mes'])
        dtable_no_sap_mes(st.session_state['conciliacion'], filters=filters[name])
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")
with tab_no_sap_mes_box:
    st.header('Facturas no encontradas en SAP por carpeta Box')
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
        name = 'no_sap_mes_box'
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            filters[name][col] = st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('dtable_'+name, col)
            )
        # filters = get_multiselect_values('dtable_'+name, FILTERS[name])
        # dtable_no_sap_box(st.session_state['conciliacion'], filters=FILTERS['no_sap_box'])
        dtable_no_sap_mes_box(st.session_state['conciliacion'], filters=filters[name])
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")
with tab_no_sap_top:
    st.header('Top proveedores con más facturas faltantes en SAP')
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
        name = 'no_sap_top'
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            filters[name][col] = st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('dtable_'+name, col)
            )
        # filters = get_multiselect_values('dtable_'+name, FILTERS[name])
        # dtable_no_sap_top_proveedores(st.session_state['conciliacion'], filters=FILTERS['no_sap_top'])
        dtable_no_sap_top(st.session_state['conciliacion'], filters=filters[name])
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")
