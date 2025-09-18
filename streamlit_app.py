import streamlit as st
import pandas as pd
from config import TAB_NAMES

st.title("Conciliación de facturas recibidas")

# generamos las pestañas 
tabs = st.tabs(TAB_NAMES)
tab_dict = {tab_name:tab for tab_name,tab in zip(TAB_NAMES,tabs)}

# pestaña de la conciliación y carga de archivos base
with tab_dict['Generar conciliación']:
    cols = st.columns(4)

    # agregamos los file uploaders
    file_fact_sat = cols[0].file_uploader('Facturas recibidas SAT',type='xlsx',accept_multiple_files=False)
    file_fact_sap = cols[1].file_uploader('Facturas SAP',type='xlsx',accept_multiple_files=False)
    file_box = cols[2].file_uploader('Box', type='xlsx', accept_multiple_files=False)
    file_cp = cols[3].file_uploader('Complementos de pago', type='xlsx', accept_multiple_files=False)

    # leemos los reportes
    if file_fact_sat:
        fact_sat = pd.read_excel(file_fact_sat, header=4)
        cols[0].write('Facturas leídas correctamente.')

    if file_fact_sap:
        fact_sap = pd.read_excel(file_fact_sap, header=9)
        cols[1].write('Facturas leídas correctamente.')
    
    if file_box:
        box = pd.read_excel(file_box, header=0)
        cols[2].write('Reporte de Box leído correctamente.')

    if file_cp:
        cp = pd.read_excel(file_cp, header=4)
        cols[3].write('Complementos de pago leídos correctamente.')