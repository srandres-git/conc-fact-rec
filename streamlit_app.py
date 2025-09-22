import streamlit as st
import pandas as pd
from analytics import create_dashboard
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
        if st.session_state.get('fact_sat') is None:
            st.session_state['fact_sat'] = depurar_sat(pd.read_excel(file_fact_sat, header=4))
            files_status['sat'] = True
            cols[0].write('Facturas leídas correctamente.')
        else:
            files_status['sat'] = True
    else:
        files_status['sat'] = False
        st.session_state['fact_sat'] = None

    if file_fact_sap:
        if st.session_state.get('fact_sap') is None:
            st.session_state['fact_sap'] = depurar_sap(pd.read_excel(file_fact_sap, header=9))
            files_status['sap'] = True
            cols[1].write('Facturas SAP leídas correctamente.')
        else:
            files_status['sap'] = True
    else:
        files_status['sap'] = False
        st.session_state['fact_sap'] = None
    
    if file_box:
        if st.session_state.get('box') is None:
            st.session_state['box'] = depurar_box(pd.read_excel(file_box, header=0))
            files_status['box'] = True
            cols[2].write('Box leídas correctamente.')
        else:
            files_status['box'] = True
    else:
        files_status['box'] = False
        st.session_state['box'] = None

    if file_cp:
        if st.session_state.get('cp') is None:
            st.session_state['cp'] = depurar_cp(pd.read_excel(file_cp, header=4))
            files_status['cp'] = True
            cols[3].write('Complementos de pago leídos correctamente.')
        else:
            files_status['cp'] = True
    else:
        files_status['cp'] = False
        st.session_state['cp'] = None

    st.session_state['conc_button'] = st.container(key='conc_button')
    st.session_state['conc_container'] = st.container(key='conc_container')
    if sum(files_status.values())==4:
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

# pestaña del dashboard
with tab_dict['Dashboard']:
    if st.session_state.get('conciliacion') is not None:
        create_dashboard(st.session_state['conciliacion'])
    else:
        st.info('Primero debes generar la conciliación en la pestaña "Generar conciliación".', icon="ℹ️")
