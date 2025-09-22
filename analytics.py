import pandas as pd
import streamlit as st

def create_dashboard(conciliacion: pd.DataFrame):
    """Crea un dashboard con estadísticas y gráficos de la conciliación."""
    st.title('Resumen de Conciliación de Facturas Recibidas')

    # Estadísticas generales
    total_facturas = len(conciliacion)
    facturas_sap = len(conciliacion[conciliacion['Estatus SAP'] != 'No está SAP'])
    facturas_box = len(conciliacion[conciliacion['Estatus Box'] == 'Encontrado'])
    facturas_cp = len(conciliacion[conciliacion['Estatus CP'] != 'No tiene CP'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Facturas", total_facturas)
    col2.metric("Facturas en SAP", facturas_sap)
    col3.metric("Facturas en Box", facturas_box)
    col4.metric("Facturas con CP", facturas_cp)

    # Gráficos de barras para estatus
    estatus_sap_counts = conciliacion['Estatus SAP'].value_counts()
    estatus_box_counts = conciliacion['Estatus Box'].value_counts()
    estatus_cp_counts = conciliacion['Estatus CP'].value_counts()

    st.subheader('Estatus en SAP')
    st.bar_chart(estatus_sap_counts)

    st.subheader('Estatus en Box')
    st.bar_chart(estatus_box_counts)

    st.subheader('Estatus en Complementos de Pago')
    st.bar_chart(estatus_cp_counts)

    # Análisis de diferencias
    st.subheader('Análisis de Diferencias entre SAT y SAP')
    diff_mxn = conciliacion['Dif. Total MXN']
    diff_xml = conciliacion['Dif. Total XML']

    st.write(f"Diferencias en MXN - Promedio: {diff_mxn.mean():.2f}, Máximo: {diff_mxn.max():.2f}")
    st.write(f"Diferencias en XML - Promedio: {diff_xml.mean():.2f}, Máximo: {diff_xml.max():.2f}")

    st.histogram(diff_mxn, bins=30, title='Distribución de Diferencias en MXN')
    st.histogram(diff_xml, bins=30, title='Distribución de Diferencias en XML')