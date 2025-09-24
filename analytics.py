import pandas as pd
import streamlit as st

from utils import dynamic_table
from config import SERVS_TRANSPORTE

def create_dashboard(conciliacion: pd.DataFrame):
    """Crea un dashboard con estadísticas y gráficos de la conciliación."""
    st.title('Resumen de Conciliación de Facturas Recibidas')

    # Resumen por comentarios de estatus

    st.header('Resumen por Comentarios de Estatus')
    dynamic_table(
        conciliacion,
        rows= ['Comentario'],
        cols= [],
        values={'Total SAT MXN':'sum','Total SAP MXN':'sum', 'Dif. Total MXN':'sum', 'UUID':'count'},
        filters={'Mes':None, 'Estatus Box':None, 'Ejecutivo CxP':None, 'Tipo de servicio':SERVS_TRANSPORTE},
        container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
            else f"{x:,}" if isinstance(x, int) \
            else f":red[{x}]" if 'Revisar' in x and isinstance(x, str) \
            else f":green[{x}]" if 'OK' in x and isinstance(x, str)\
            else x
    )