import pandas as pd
import streamlit as st
from config import FILTERS
from utils import multiselect_key, get_multiselect_values

# from utils import multiselect_key, update_filters
# from config import FILTERS

# def create_dashboard(conciliacion: pd.DataFrame):
#     """Crea un dashboard con estadísticas y gráficos de la conciliación."""
#     st.title('Resumen de Conciliación de Facturas Recibidas')
#     # TODO: agregar gráficos
#     if 'dashboard_containers' not in st.session_state:
#         st.session_state['dashboard_containers'] = {
#             'estatus': st.container(),
#             'no_sap_mes': st.container(),
#             'no_sap_mes_box': st.container(),
#             'no_sap_top': st.container()
#         }

#     with st.session_state['dashboard_containers']['estatus']:
#         # create the multiselect filters
#         st.header('Resumen por Comentarios de Estatus')
#         for col, preselected in FILTERS['estatus'].items():
#             options = conciliacion[col].dropna().unique().tolist()
#             default = [val for val in preselected if val in options] if preselected else None
#             st.multiselect(
#                 f'{col}',
#                 options=options,
#                 default=default,
#                 key=multiselect_key('dtable_estatus', col)
#             )
#         filters = {col: st.session_state[multiselect_key('dtable_estatus', col)] for col in FILTERS['estatus'].keys()}
#         dtable_estatus(conciliacion, filters=filters)
#     with st.session_state['dashboard_containers']['no_sap_mes']:
#         st.header('Facturas no encontradas en SAP por Mes')
#         for col, preselected in FILTERS['no_sap_mes'].items():
#             options = conciliacion[col].dropna().unique().tolist()
#             default = [val for val in preselected if val in options] if preselected else None
#             st.multiselect(
#                 f'{col}',
#                 options=options,
#                 default=default,
#                 key=multiselect_key('dtable_no_sap_mes', col)
#             )
#         dtable_no_sap_mes(conciliacion, filters=FILTERS['no_sap_mes'])
#     with st.session_state['dashboard_containers']['no_sap_mes_box']:
#         st.header('Facturas no encontradas en SAP por Mes y Estatus en Box')
#         for col, preselected in FILTERS['no sap_mes_box'].items():
#             options = conciliacion[col].dropna().unique().tolist()
#             default = [val for val in preselected if val in options] if preselected else None
#             st.multiselect(
#                 f'{col}',
#                 options=options,
#                 default=default,
#                 key=multiselect_key('dtable_no_sap_mes_box', col)
#             )
#         dtable_no_sap_mes_box(conciliacion, filters=FILTERS['no sap_mes_box'])
#     with st.session_state['dashboard_containers']['no_sap_top']:
#         st.header('Facturas no encontradas en SAP por Proveedor (Top 35)')
#         for col, preselected in FILTERS['no_sap_top'].items():
#             options = conciliacion[col].dropna().unique().tolist()
#             default = [val for val in preselected if val in options] if preselected else None
#             st.multiselect(
#                 f'{col}',
#                 options=options,
#                 default=default,
#                 key=multiselect_key('dtable_no_sap_top', col)
#             )
#         dtable_no_sap_top(conciliacion, filters=FILTERS['no_sap_top'], top_n=35)

@st.experimental_fragment
def dtable_estatus(conciliacion: pd.DataFrame, name = 'estatus'):
    """Realiza la tabla dinámica de resumen de comentarios de estatus."""
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:        
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('ms_'+name, col)
            )
        filters = get_multiselect_values('ms_'+name, FILTERS[name])
        pivot_df = pivot_table(
            conciliacion,
            rows= ['Comentario'],
            cols= [],
            values={'Total SAT MXN':'sum','Total SAP MXN':'sum', 'Dif. Total MXN':'sum', 'UUID':'count'},
            filters=filters,
            format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
                else f"{x:,}" if isinstance(x, int) \
                else f":red[{x}]" if 'Revisar' in x and isinstance(x, str) \
                else f":green[{x}]" if 'OK' in x and isinstance(x, str)\
                else x,
            sort_args={'by': 'Total SAT MXN', 'ascending':False},
        )
        st.table(pivot_df, border='horizontal')
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")
   

@st.experimental_fragment
def dtable_no_sap_mes(conciliacion: pd.DataFrame, name = 'no_sap_mes'):
    """Realiza la tabla dinámica de facturas faltantes en SAP por mes."""
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('ms_'+name, col)
            )
        filters = get_multiselect_values('ms_'+name, FILTERS[name])
        pivot_df = pivot_table(
            conciliacion,
            rows= ['Mes'],
            cols= [],
            values={'Total SAT MXN':'sum','UUID':'count'},
            filters=filters,
            format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
                else f"{x:,}" if isinstance(x, int) \
                else x,
            sort_args={'by': 'Total SAT MXN', 'ascending':False},
        )
        st.table(pivot_df, border='horizontal')
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")

@st.experimental_fragment
def dtable_no_sap_mes_box(conciliacion: pd.DataFrame, name = 'no_sap_mes_box'):
    """Realiza la tabla dinámica de facturas faltantes en SAP por mes y estatus en Box."""
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('ms_'+name, col)
            )
        filters = get_multiselect_values('ms_'+name, FILTERS[name])
        pivot_df = pivot_table(
            conciliacion,
            rows= ['Estatus Box'],
            cols= ['Mes'],
            values={'Total SAT MXN':'sum'},
            filters=filters,
            format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
                else f"{x:,}" if isinstance(x, int) \
                else x
        )
        st.table(pivot_df, border='horizontal')
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")

@st.experimental_fragment
def dtable_no_sap_top(conciliacion: pd.DataFrame, name = 'no_sap_top', top_n:int=35):
    """"Tabla dinámica de facturas faltantes en SAP por Emisor Nombre (top N)."""
    if 'conciliacion' in st.session_state and st.session_state['conciliacion'] is not None:
        for col, preselected in FILTERS[name].items():
            options = st.session_state['conciliacion'][col].dropna().unique().tolist()
            default = [val for val in preselected if val in options] if preselected else None
            st.multiselect(
                f'{col}',
                options=options,
                default=default,
                key=multiselect_key('ms_'+name, col)
            )
        filters = get_multiselect_values('ms_'+name, FILTERS[name])
        pivot_df = pivot_table(
            conciliacion,
            rows= ['Emisor Nombre'],
            cols= [],
            values={'Total SAT MXN':'sum','UUID':'count'},
            filters=filters,
            format_func= lambda x: f"{x:,.2f}" if isinstance(x, float)\
                else f"{x:,}" if isinstance(x, int) \
                else x,
            sort_args={'by': 'Total SAT MXN', 'ascending':False},
            top_n=top_n,
        )
        st.table(pivot_df, border='horizontal')
    else:
        st.info('Por favor, genere o cargue una conciliación para ver el dashboard.', icon="ℹ️")

def pivot_table(
    df: pd.DataFrame,
    rows: list[str],
    cols: list[str],
    values: dict[str, str],  # {column: aggfunc}
    filters: dict[str, list], # {column: list of preselected values}
    format_func: callable = None,
    sort_args: dict = None,
    top_n: int = None,
    bottom_n: int = None,
):
    """
    Create a dynamic pivot-like table.

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
    # --- Filtering ---
    filtered_df = df[cols+rows+list(values.keys())+list(filters.keys())].copy()
    for col, selected_vals in filters.items():
        unique_vals = filtered_df[col].dropna().unique().tolist()
        if selected_vals:
            selected_vals = [val for val in selected_vals if val in unique_vals]# correct preselected to make sure the value exists
            filtered_df[filtered_df[col].isin(selected_vals)]

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

    return pivot_df