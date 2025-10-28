import streamlit as st
import pandas as pd
from analytics import create_dashboard
# pestaña del dashboard

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
if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
    # Creamos el dashboard sólo una vez y lo mantenemos entre actualizaciones
    if not st.session_state.get('dashboard_loaded', False):
        create_dashboard(st.session_state['conciliacion'])
        st.session_state['dashboard_loaded'] = True
    else:
        # Re-renderizamos los contenedores persistentes si ya está cargado
        dashboard_containers = st.session_state.get('dashboard_containers', {})
        if dashboard_containers:
            with dashboard_containers['estatus']:
                pass  # el contenido ya existe
            with dashboard_containers['no_sap_mes']:
                pass
            with dashboard_containers['no_sap_mes_box']:
                pass
            with dashboard_containers['no_sap_top']:
                pass
else:
    st.info(
        'Primero debes generar la conciliación en la pestaña "Generar conciliación" '
        'o cargar una conciliación previa.',
        icon="ℹ️"
    )