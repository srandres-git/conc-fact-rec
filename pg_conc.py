import streamlit as st
import pandas as pd
from config import EXPECTED_COLS
from conc import conciliar
from clean_data import read_excel_file
from utils import get_provs

st.set_page_config(layout="wide")
st.title("Conciliación de facturas recibidas")

cols = st.columns(4)
st.session_state['conc_button'] = st.container(key='conc_button')
st.session_state['conc_container'] = st.container(key='conc_container')
# si no existen las variables de sesión, las inicializamos
for var in ['fact_sat', 'fact_sap', 'box', 'cp', 'conciliacion', ]:
    if var not in st.session_state:
        st.session_state[var] = None

# SAP auth session keys
if 'sap_authenticated' not in st.session_state:
    st.session_state['sap_authenticated'] = False
if 'sap_username_saved' not in st.session_state:
    st.session_state['sap_username_saved'] = ''
if 'sap_password_saved' not in st.session_state:
    st.session_state['sap_password_saved'] = ''

# Authentication form: validate credentials before showing uploaders and conciliation
if not st.session_state['sap_authenticated']:
    st.markdown('### Autenticación SAP requerida')
    with st.form(key='sap_auth_form'):
        user = st.text_input('Usuario SAP', key='sap_username_input')
        pwd = st.text_input('Contraseña SAP', type='password', key='sap_password_input')
        submit = st.form_submit_button('Validar credenciales SAP')
    if submit:
        with st.spinner('Validando credenciales...'):
            # use a tiny sample to validate credentials quickly
            test = get_provs(['XEXX010101000'], username=user, password=pwd, bucket_size=1)
            if test is None:
                st.error('Credenciales inválidas o error de conexión. Intenta de nuevo.', icon='❌')
                st.session_state['sap_authenticated'] = False
            else:
                st.success('Autenticación SAP exitosa.', icon='✅')
                st.session_state['sap_authenticated'] = True
                st.session_state['sap_username_saved'] = user
                st.session_state['sap_password_saved'] = pwd
    else:
        st.info('Introduce tus credenciales SAP y pulsa "Validar credenciales SAP" para continuar.')
    st.stop()

@st.fragment
def create_file_uploader(name: str, label:str, header:int=0):
    """Crea un file uploader con el nombre y etiqueta especificados. Ejecuta la función read_excel_file al cargar un archivo."""
    st.file_uploader(label, type='xlsx', accept_multiple_files=False, key=name+'_uploader')
    if st.session_state.get(name+'_uploader') is not None:
        st.session_state[name] = read_excel_file(
            st.session_state[name+'_uploader'],
            session_name=name,
            expected_columns=EXPECTED_COLS[name],
            header=header
        )
        

# leemos los reportes y agregamos los file uploaders
with cols[0]:
    if st.session_state.get('fact_sat') is None:
        create_file_uploader('fact_sat', 'Facturas recibidas SAT', header=4)
with cols[1]:
    if st.session_state.get('fact_sap') is None:
        create_file_uploader('fact_sap', 'Facturas SAP', header=9)
with cols[2]:
    if st.session_state.get('box') is None:
        create_file_uploader('box', 'Box', header=0)
with cols[3]:
    if st.session_state.get('cp') is None:
        create_file_uploader('cp', 'Complementos de pago', header=4)

with st.session_state['conc_button']:
    # if st.session_state.get('conciliacion') is None:
        conciliacion = st.button('Conciliar', on_click=conciliar,)
                                # args=(st.session_state['fact_sat'], 
                                #         st.session_state['fact_sap'], 
                                #         st.session_state['box'], 
                                #         st.session_state['cp'],))

if st.session_state.get('conciliacion') is not None:
    with st.session_state['conc_container']:
        st.write(st.session_state['conciliacion'])
if st.session_state.get('output_file') is not None:
    st.session_state['output_file'].seek(0)  # move to the beginning of the BytesIO buffer
    st.download_button('Descargar reporte de conciliación', data=st.session_state['output_file'], file_name='Conciliacion_Facturas_Recibidas.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
