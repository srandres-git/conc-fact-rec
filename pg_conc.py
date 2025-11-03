import streamlit as st
import pandas as pd
from config import EXPECTED_COLS
from conc import conciliar
from clean_data import read_excel_file

st.set_page_config(layout="wide")
st.title("Conciliación de facturas recibidas")

cols = st.columns(4)
st.session_state['conc_button'] = st.container(key='conc_button')
st.session_state['conc_container'] = st.container(key='conc_container')
st.session_state['fact_sat'] = None
st.session_state['fact_sap'] = None
st.session_state['box'] = None
st.session_state['cp'] = None

@st.fragment
def create_file_uploader(name: str, label:str, header:int=0):
    """Crea un file uploader con el nombre y etiqueta especificados. Ejecuta la función read_excel_file al cargar un archivo."""
    st.file_uploader(label, type='xlsx', accept_multiple_files=False, key=name+'_uploader')
    if st.session_state.get(name+'_uploader') is not None:
        return read_excel_file(
            st.session_state[name+'_uploader'],
            session_name=name,
            expected_columns=EXPECTED_COLS[name],
            header=header
        )
        

# leemos los reportes y agregamos los file uploaders
with cols[0]:
    st.session_state['fact_sat'] =  create_file_uploader('fact_sat', 'Facturas recibidas SAT', header=4)
with cols[1]:
    st.session_state['fact_sap'] = create_file_uploader('fact_sap', 'Facturas SAP', header=9)
with cols[2]:
    st.session_state['box'] = create_file_uploader('box', 'Box', header=0)
with cols[3]:
    st.session_state['cp'] = create_file_uploader('cp', 'Complementos de pago', header=4)

with st.session_state['conc_button']:
    conciliacion = st.button('Conciliar', on_click=conciliar,
                            args=(st.session_state['fact_sat'], 
                                    st.session_state['fact_sap'], 
                                    st.session_state['box'], 
                                    st.session_state['cp'],))

if st.session_state.get('conciliacion') is not None:
    with st.session_state['conc_container']:
        st.write(st.session_state['conciliacion'])
if st.session_state.get('output_file') is not None:
    st.session_state['output_file'].seek(0)  # move to the beginning of the BytesIO buffer
    st.download_button('Descargar reporte de conciliación', data=st.session_state['output_file'], file_name='Conciliacion_Facturas_Recibidas.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
