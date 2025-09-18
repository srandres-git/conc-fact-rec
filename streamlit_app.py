import streamlit as st
import pandas as pd

st.title("Conciliación de facturas recibidas")
file_fact_sat = st.file_uploader('Facturas recibidas SAT',type='xlsx',accept_multiple_files=False)

if file_fact_sat:
    st.write('Leyendo reporte de facturas SAT...')
    fact_sat = pd.read_excel(file_fact_sat, header=4)
    st.write('Facturas leídas correctamente.')