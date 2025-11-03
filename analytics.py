import pandas as pd
import streamlit as st
from config import FILTERS, MONTH_ORDER
from utils import multiselect_key, get_multiselect_values

@st.fragment
def dtable_estatus(conciliacion: pd.DataFrame, name = 'estatus'):
    """Realiza la tabla dinámica de resumen de comentarios de estatus."""  
    with st.expander("Filtros", icon='⚙️'):
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
        total_row=True,
    )
    st.table(pivot_df, border='horizontal')
   

@st.fragment
def dtable_no_sap_mes(conciliacion: pd.DataFrame, name = 'no_sap_mes'):
    """Realiza la tabla dinámica de facturas faltantes en SAP por mes."""
    with st.expander("Filtros", icon='⚙️'):
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
        sort_args={'by': 'Total SAT MXN', 'ascending':False},
        total_row=True,
    )
    pivot_df['Mes'] = pd.Categorical(pivot_df['Mes'], categories=MONTH_ORDER+['Total'], ordered=True)
    pivot_df.set_index('Mes', inplace=True)
    pivot_df.sort_index(inplace=True)
    st.table(pivot_df.style.format({
        "Total SAT MXN": "{:,.2f}",
        "UUID": "{:,}"
    }), border='horizontal')
    #quitamos 'Total' de la gráfica
    pivot_df = pivot_df[pivot_df.index != 'Total']
    st.bar_chart(pivot_df, y='Total SAT MXN', sort=True)

    
@st.fragment
def dtable_no_sap_mes_box(conciliacion: pd.DataFrame, name = 'no_sap_mes_box'):
    """Realiza la tabla dinámica de facturas faltantes en SAP por mes y estatus en Box."""
    with st.expander("Filtros", icon='⚙️'):
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
        total_col=True,
        total_row=True,
        format_func= lambda x: f"{x:,.2f}" if isinstance(x, float) \
            else f"{x:,}" if isinstance(x, int) \
            else x
    ).sort_index(axis=1, level=1, key=lambda x: pd.Categorical(x, categories=['']+MONTH_ORDER, ordered=True))
    st.table(pivot_df, border='horizontal')

@st.fragment
def dtable_no_sap_top(conciliacion: pd.DataFrame, name = 'no_sap_top', top_n:int=35):
    """"Tabla dinámica de facturas faltantes en SAP por Emisor Nombre (top N)."""
    with st.expander("Filtros", icon='⚙️'):
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
        total_row=True,
    )
    st.table(pivot_df, border='horizontal')

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
    total_row: bool = False,
    total_col: bool = False,
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
        total_row: Whether to add a total row
        total_col: Whether to add a total column
    """
    # --- Filtering ---
    filtered_df = df[cols+rows+list(values.keys())+list(filters.keys())].copy()
    for col, selected_vals in filters.items():
        unique_vals = filtered_df[col].dropna().unique().tolist()
        if selected_vals:
            selected_vals = [val for val in selected_vals if val in unique_vals]# correct preselected to make sure the value exists
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

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
    # Add total row if specified
    if total_row:
        total_series = pd.DataFrame(pivot_df.sum(numeric_only=True)).T
        total_series.index = pd.Index(['Total'], name=pivot_df.index.name)
        pivot_df = pd.concat([pivot_df, total_series])
    # Add total column if specified
    if total_col:
        pivot_df['Total'] = pivot_df.sum(axis=1, numeric_only=True)
    # Reset index and start it on 1 so it shows nicely in Streamlit
    pivot_df = pivot_df.reset_index()
    pivot_df.index += 1
     # Apply formatting function if provided
    if format_func:
        pivot_df = pivot_df.applymap(format_func)

    return pivot_df