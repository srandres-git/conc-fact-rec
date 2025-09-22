import pandas as pd
import streamlit as st

def create_dashboard(conciliacion: pd.DataFrame):
    """Crea un dashboard con estadísticas y gráficos de la conciliación."""
    st.title('Resumen de Conciliación de Facturas Recibidas')

    # Estadísticas generales
    total_facturas = len(conciliacion)
    facturas_no_sap = len(conciliacion[conciliacion['Comentario']=='Revisar // Vigente SAT - No está en SAP'])
    facturas_no_box = len(conciliacion[conciliacion['Estatus Box'] == 'No está Box'])
    facturas_no_cp = len(conciliacion[conciliacion['Comentario'] == 'Revisar // Vigente SAT - Pagado SAP - Sin CP'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Facturas", total_facturas)
    col2.metric("Faltantes SAP", facturas_no_sap)
    col3.metric("Faltantes Box", facturas_no_box)
    col4.metric("Pagadas sin CP", facturas_no_cp)

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
