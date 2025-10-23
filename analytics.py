import pandas as pd
import streamlit as st

from utils import dynamic_table
from config import SERVS_TRANSPORTE

def create_dashboard(conciliacion: pd.DataFrame):
    """Crea un dashboard con estadísticas y gráficos de la conciliación."""
    st.title('Resumen de Conciliación de Facturas Recibidas')
    # TODO: agregar gráficos
    if 'dashboard_containers' not in st.session_state:
        st.session_state['dashboard_containers'] = {
            'estatus': st.container(),
            'no_sap_mes': st.container(),
            'no_sap_mes_box': st.container(),
            'no_sap_top': st.container()
        }

    with st.session_state['dashboard_containers']['estatus']:
        dtable_estatus(conciliacion)
    with st.session_state['dashboard_containers']['no_sap_mes']:
        dtable_no_sap_mes(conciliacion)
    with st.session_state['dashboard_containers']['no_sap_mes_box']:
        dtable_no_sap_mes_box(conciliacion)
    with st.session_state['dashboard_containers']['no_sap_top']:
        dtable_no_sap_top(conciliacion)

def dtable_estatus(conciliacion: pd.DataFrame):
    """Realiza la tabla dinámica de resumen de comentarios de estatus."""
    st.header('Resumen por Comentarios de Estatus')
    dynamic_table(
        conciliacion,
        rows= ['Comentario'],
        cols= [],
        values={'Total SAT MXN':'sum','Total SAP MXN':'sum', 'Dif. Total MXN':'sum', 'UUID':'count'},
        filters={'Tipo de servicio':SERVS_TRANSPORTE, 'Mes':None, 'Estatus Box':None, 'Ejecutivo CxP':None, },
        name='dtable_estatus',
        # container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
            else f"{x:,}" if isinstance(x, int) \
            else f":red[{x}]" if 'Revisar' in x and isinstance(x, str) \
            else f":green[{x}]" if 'OK' in x and isinstance(x, str)\
            else x,
        sort_args={'by': 'Total SAT MXN', 'ascending':False},
    )

def dtable_no_sap_mes(conciliacion: pd.DataFrame):
    """Realiza la tabla dinámica de facturas faltantes en SAP por mes."""
    st.header('Facturas no encontradas en SAP por Mes')
    # se preselecciona el comentario 'Revisar // Vigente SAT - No está en SAP'
    dynamic_table(
        conciliacion,
        rows= ['Mes'],
        cols= [],
        values={'Total SAT MXN':'sum','UUID':'count'},
        filters={'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Estatus Box':None, 'Ejecutivo CxP':None,},
        name='dtable_no_sap_mes',
        # container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
            else f"{x:,}" if isinstance(x, int) \
            else x,
        sort_args={'by': 'Total SAT MXN', 'ascending':False},
    )

def dtable_no_sap_mes_box(conciliación):
    """Realiza la tabla dinámica de facturas faltantes en SAP por mes y estatus en Box."""
    st.header('Facturas no encontradas en SAP por Mes y Estatus en Box')
    # se preselecciona el comentario 'Revisar // Vigente SAT - No está en SAP'
    dynamic_table(
        conciliación,
        rows= [ 'Estatus Box'],
        cols= ['Mes'],
        values={'Total SAT MXN':'sum',},
        filters={'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Ejecutivo CxP':None,},
        name='dtable_no_sap_mes_box',
        # container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
            else f"{x:,}" if isinstance(x, int) \
            else x,
        # sort_args={'by': 'Mes', 'ascending':False},
    )

def dtable_no_sap_top(conciliacion: pd.DataFrame, top_n:int=35):
    """"Tabla dinámica de facturas faltantes en SAP por Emisor Nombre (top N)."""
    st.header(f'Facturas no encontradas en SAP por Proveedor (Top {top_n})')
    # se preselecciona el comentario 'Revisar // Vigente SAT - No está en SAP'
    dynamic_table(
        conciliacion,
        rows= ['Emisor Nombre'],
        cols= [],
        values={'Total SAT MXN':'sum','UUID':'count'},
        filters={'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Mes':None, 'Estatus Box':None, 'Ejecutivo CxP':None,},
        name='dtable_no_sap_top',
        # container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float)\
            else f"{x:,}" if isinstance(x, int) \
            else x,
        sort_args={'by': 'Total SAT MXN', 'ascending':False},
        top_n=top_n,
    )