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
    placeholder_sat = cols[0].empty().container() # container del mensaje de actualización

    file_fact_sap = cols[1].file_uploader('Facturas SAP',type='xlsx',accept_multiple_files=False)
    placeholder_sap = cols[1].empty().container()

    file_box = cols[2].file_uploader('Box', type='xlsx', accept_multiple_files=False)
    placeholder_box = cols[2].empty().container()

    file_cp = cols[3].file_uploader('Complementos de pago', type='xlsx', accept_multiple_files=False)
    placeholder_cp = cols[3].empty().container()

    # leemos los reportes
    if file_fact_sat:
        placeholder_sat.write('Leyendo reporte de facturas SAT...')
        fact_sat = pd.read_excel(file_fact_sat, header=4)
        placeholder_sat.write('Facturas leídas correctamente.')

    if file_fact_sap:
        placeholder_sap.write('Leyendo saldos de facturas SAP...')
        fact_sap = pd.read_excel(file_fact_sap, header=9)
        placeholder_sap.write('Facturas leídas correctamente.')
    
    if file_box:
        placeholder_box.write('Leyendo reporte de Box...')
        box = pd.read_excel(file_box, header=0)
        placeholder_box.write('Reporte de Box leído correctamente.')

    if file_cp:
        placeholder_cp.write('Leyendo complementos de pago...')
        cp = pd.read_excel(file_cp, header=4)
        placeholder_cp('Complementos de pago leídos correctamente.')