import pandas as pd
import streamlit as st

from utils import multiselect_key, update_filters
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
    filters={'Tipo de servicio':SERVS_TRANSPORTE, 'Mes':None, 'Estatus Box':None, 'Ejecutivo CxP':None, }
    name='dtable_estatus'
    filters = update_filters(filters,name)
    dynamic_table(
        conciliacion,
        rows= ['Comentario'],
        cols= [],
        values={'Total SAT MXN':'sum','Total SAP MXN':'sum', 'Dif. Total MXN':'sum', 'UUID':'count'},
        filters=filters,
        name='dtable_estatus',
        header='Resumen por Comentarios de Estatus',
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
    filters={'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Estatus Box':None, 'Ejecutivo CxP':None,}
    name='dtable_no_sap_mes'
    filters = update_filters(filters,name)
    # se preselecciona el comentario 'Revisar // Vigente SAT - No está en SAP'
    dynamic_table(
        conciliacion,
        rows= ['Mes'],
        cols= [],
        values={'Total SAT MXN':'sum','UUID':'count'},
        filters=filters,
        name=name,
        header='Facturas no encontradas en SAP por Mes',
        # container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
            else f"{x:,}" if isinstance(x, int) \
            else x,
        sort_args={'by': 'Total SAT MXN', 'ascending':False},
    )

def dtable_no_sap_mes_box(conciliación):
    """Realiza la tabla dinámica de facturas faltantes en SAP por mes y estatus en Box."""
    filters={'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Ejecutivo CxP':None,}
    name='dtable_no_sap_mes_box'
    filters = update_filters(filters,name)
    # se preselecciona el comentario 'Revisar // Vigente SAT - No está en SAP'
    dynamic_table(
        conciliación,
        rows= [ 'Estatus Box'],
        cols= ['Mes'],
        values={'Total SAT MXN':'sum',},
        filters=filters,
        name=name,
        header='Facturas no encontradas en SAP por Mes y Estatus en Box',
        # container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
            else f"{x:,}" if isinstance(x, int) \
            else x,
        # sort_args={'by': 'Mes', 'ascending':False},
    )

def dtable_no_sap_top(conciliacion: pd.DataFrame, top_n:int=35):
    """"Tabla dinámica de facturas faltantes en SAP por Emisor Nombre (top N)."""
    filters={'Comentario':['Revisar // Vigente SAT - No está en SAP'],'Tipo de servicio':SERVS_TRANSPORTE, 'Mes':None, 'Estatus Box':None, 'Ejecutivo CxP':None,}
    name='dtable_no_sap_top'
    filters = update_filters(filters,name)
    # se preselecciona el comentario 'Revisar // Vigente SAT - No está en SAP'
    dynamic_table(
        conciliacion,
        rows= ['Emisor Nombre'],
        cols= [],
        values={'Total SAT MXN':'sum','UUID':'count'},
        filters=filters,
        name=name,
        header=f'Facturas no encontradas en SAP por Proveedor (Top {top_n})',
        # container=st.container(),
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float)\
            else f"{x:,}" if isinstance(x, int) \
            else x,
        sort_args={'by': 'Total SAT MXN', 'ascending':False},
        top_n=top_n,
    )

def dynamic_table(
    df: pd.DataFrame,
    rows: list[str],
    cols: list[str],
    values: dict[str, str],  # {column: aggfunc}
    filters: dict[str, list],
    name: str,
    header: str,
    # container,
    format_func: callable = None,
    sort_args: dict = None,
    top_n: int = None,
    bottom_n: int = None,
):
    """
    Create a dynamic pivot-like table in Streamlit with filters.

    Args:
        df: DataFrame
        rows: list of columns to use as rows
        cols: list of columns to use as columns
        values: dict of {column: aggfunc}
        filters: dict of {column: list of preselected values}
        name: Name of the table (used for generating unique keys)
        container: Streamlit container to display the table
        format_func: Optional function to format cell values
        sort_args: Optional keyword arguments for sorting the table
        top_n: Optional int to show only top N rows
        bottom_n: Optional int to show only bottom N rows
    """
    if f"table_container_{name}" not in st.session_state:
        st.session_state[f"table_container_{name}"] = st.container()
    with st.session_state[f"table_container_{name}"]:
        st.header(header)
    # --- Filtering widgets ---
    filtered_df = df.copy()
    for col, preselected in filters.items():
        unique_vals = df[col].dropna().unique().tolist()
        if preselected:
            preselected = [val for val in preselected if val in unique_vals]# correct preselected to make sure the value exists
        ms_key = multiselect_key(name, col)
        with st.session_state.get(f"filter_container_{name}", st.container()):
            selected = st.multiselect(
                f"{col}",
                options=unique_vals,
                default=preselected,
                # generate a unique key using the name and column name
                key=ms_key
            )
        # display the multiselect with the selected values        
        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]

    # --- Pivot table ---
    pivot_df = pd.pivot_table(
        filtered_df,
        index=rows if rows else None,
        columns=cols if cols else None,
        values=list(values.keys()),
        aggfunc=values,
        fill_value=0
    )
    # sort the table if args provided
    if sort_args:
        pivot_df = pivot_df.sort_values(**sort_args)
    # show only top N rows if specified
    if top_n:
        pivot_df = pivot_df.head(top_n)
    # show only bottom N rows if specified
    if bottom_n:
        pivot_df = pivot_df.tail(bottom_n)
    # Reset index and start it on 1 so it shows nicely in Streamlit
    pivot_df = pivot_df.reset_index()
    pivot_df.index += 1
     # Apply formatting function if provided
    if format_func:
        pivot_df = pivot_df.applymap(format_func)

    # --- Display persistent container ---    

    with st.session_state[f"table_container_{name}"]:
        st.table(pivot_df, border='horizontal')

    # Keep the resulting table in memory for possible later use
    st.session_state[name] = pivot_df

