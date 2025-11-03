import streamlit as st
import pandas as pd
from config import TAB_NAMES, EXPECTED_COLS
from conc import conciliar
from utils import read_excel_file

st.set_page_config(layout="wide")
st.title("Conciliación de facturas recibidas")

cols = st.columns(4)

file_fact_sat = cols[0].file_uploader('Facturas recibidas SAT',type='xlsx',accept_multiple_files=False)
file_fact_sap = cols[1].file_uploader('Facturas SAP',type='xlsx',accept_multiple_files=False)
file_box = cols[2].file_uploader('Box', type='xlsx', accept_multiple_files=False)
file_cp = cols[3].file_uploader('Complementos de pago', type='xlsx', accept_multiple_files=False)

# leemos los reportes y agregamos los file uploaders
with cols[0]:
    if file_fact_sat:
        read_excel_file(
            file_fact_sat,
            session_name='fact_sat',
            expected_columns=EXPECTED_COLS['fact_sat'],
            header=4
        )
with cols[1]:
    if file_fact_sap:
        read_excel_file(
            file_fact_sap,
            session_name='fact_sap',
            expected_columns=EXPECTED_COLS['fact_sap'],
            header=9
        )

with cols[2]:
    if file_box:
        read_excel_file(
            file_box,
            session_name='box',
            expected_columns=EXPECTED_COLS['box'],
            header=0
        )

with cols[3]:
    if file_cp:
        read_excel_file(
            file_cp,
            session_name='cp',
            expected_columns=EXPECTED_COLS['cp'],
            header=4
        )


st.session_state['conc_button'] = st.container(key='conc_button')
st.session_state['conc_container'] = st.container(key='conc_container')
if st.session_state.get('fact_sat') is not None and \
    st.session_state.get('fact_sap') is not None and \
    st.session_state.get('box') is not None and \
    st.session_state.get('cp') is not None:
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


