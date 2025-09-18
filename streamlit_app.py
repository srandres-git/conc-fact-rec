import streamlit as st
import pandas as pd
from config import TAB_NAMES
from conc import conciliar
from clean_data import depurar_box, depurar_cp, depurar_sap, depurar_sat

st.title("Conciliación de facturas recibidas")

# generamos las pestañas 
tabs = st.tabs(TAB_NAMES)
tab_dict = {tab_name:tab for tab_name,tab in zip(TAB_NAMES,tabs)}

# pestaña de la conciliación y carga de archivos base
with tab_dict['Generar conciliación']:
    cols = st.columns(4)

    files_status = {file:False for file in ['sat','sap','box','cp']}
    # agregamos los file uploaders
    file_fact_sat = cols[0].file_uploader('Facturas recibidas SAT',type='xlsx',accept_multiple_files=False)
    file_fact_sap = cols[1].file_uploader('Facturas SAP',type='xlsx',accept_multiple_files=False)
    file_box = cols[2].file_uploader('Box', type='xlsx', accept_multiple_files=False)
    file_cp = cols[3].file_uploader('Complementos de pago', type='xlsx', accept_multiple_files=False)

    # leemos los reportes
    if file_fact_sat:
        files_status['sat'] = False
        fact_sat = pd.read_excel(file_fact_sat, header=4)
        fact_sat = depurar_sat(fact_sat)
        files_status['sat'] = True
        cols[0].write('Facturas leídas correctamente.')

    if file_fact_sap:
        files_status['sap'] = False
        fact_sap = pd.read_excel(file_fact_sap, header=9)
        fact_sap = depurar_sap(fact_sap)
        files_status['sap'] = True
        cols[1].write('Facturas leídas correctamente.')
    
    if file_box:
        files_status['box'] = False
        box = pd.read_excel(file_box, header=0)
        box = depurar_box(box)
        files_status['box'] = True
        cols[2].write('Reporte de Box leído correctamente.')

    if file_cp:
        files_status['cp'] = False
        cp = pd.read_excel(file_cp, header=4)
        cp = depurar_cp(cp)
        files_status['cp'] = True
        cols[3].write('Complementos de pago leídos correctamente.')

    st.session_state['conc_button'] = st.container(key='conc_button')
    st.session_state['conc'] = st.container(key='conc')
    if sum(files_status.values())==4:
        with st.session_state['conc_button']:
            conciliacion = st.button('Conciliar', on_click=conciliar, args=[fact_sat,fact_sap,box,cp])
