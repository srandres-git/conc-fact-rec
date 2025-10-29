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
filters = {
    'estatus':{},
    'no_sap_mes':{},
    'no_sap_mes_box':{},
    'no_sap_top':{}
}
with tab_estatus:
    st.header('Resumen por Comentarios de Estatus')
    dtable_estatus(st.session_state['conciliacon'])
with tab_no_sap_mes:
    st.header('Facturas no encontradas en SAP por Mes')
    dtable_no_sap_mes(st.session_state['conciliacion'])
with tab_no_sap_mes_box:
    st.header('Facturas no encontradas en SAP por carpeta Box')
    dtable_no_sap_mes_box(st.session_state['conciliacion'])
with tab_no_sap_top:
    st.header('Top proveedores con más facturas faltantes en SAP')
    dtable_no_sap_top(st.session_state['conciliacion'])
