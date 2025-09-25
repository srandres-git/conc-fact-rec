import re
import numpy as np
import pandas as pd
import requests
import streamlit as st

from config import COLS_SERVICE

def clean_dtypes(df: pd.DataFrame, num_cols, date_cols, date_format=None):
    """Corrección de los tipos de datos, según la lista de columnas numéricas o de fecha."""
    # obtenemos las columnas que tienen tipo numérico pero no están en num_cols
    other_num_cols = [col for col in df.select_dtypes(include=['number']).columns if col not in num_cols + date_cols]
    
    # en num_cols, reemplazamos NaN por 0
    df[num_cols] = df[num_cols].fillna(0)
    # las que no son num_cols ni date_cols, reemplazamos NaN por cadena vacía
    df = df.fillna({col: '' for col in df.columns if col not in num_cols + date_cols})
    
    # transformamos a numérico las columnas en num_cols
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='raise')
    # transformamos a texto las columnas que están en other_num_cols y quitamos decimales
    df[other_num_cols] = df[other_num_cols].apply(lambda x: x.astype(str).str.split('.').str[0])
    # transformamos a fecha las columnas en date_cols
    if date_format:
        df[date_cols] = df[date_cols].apply(lambda x: pd.to_datetime(x, format=date_format, errors='coerce'))
    else:
        df[date_cols] = df[date_cols].apply(pd.to_datetime, errors='coerce')
    # las columnas restantes a texto
    df = df.astype({col: str for col in df.columns if col not in num_cols + date_cols + other_num_cols})
    
    return df

def sort_df(df:pd.DataFrame, col:str, values:list, drop_dup_col:str=''):
    """Ordena un DataFrame según una columna y una lista de valores específicos en el orden deseado.
    Borra duplicados en drop_dup_col si se especifica."""
    order_map = {value: index for index, value in enumerate(values)}
    # valores deconocidos -> última posición (se mandan al final)
    df['sort_key'] = df[col].map(order_map).fillna(len(values))
    df = df.sort_values(by='sort_key').drop(columns=['sort_key'])
    if drop_dup_col:
        df = df.drop_duplicates(subset=drop_dup_col, keep='first').reset_index(drop=True)
    return df

def find_service(row):
    """
    Encuentra el número de servicio en una cadena de texto s:
    formato AA-XXXXXX
    """    
    # Expresión regular para el patrón AA-XXXXXX
    pattern = rf'(2[12345]+)[ ]?[- _‐]+[ ]?(\d{{4,6}})'
    # Buscar el patrón en el texto de cada columna de la lista cols_service
    for col in COLS_SERVICE:
        matches = re.findall(pattern, row[col])
        if len(matches)>0:
            # regresar solo matches distintos rellenando el segundo grupo con ceros a la izquierda hasta completar 6 dígitos
            return '/'.join(set([f'{m[0]}-{m[1].zfill(6)}' for m in matches]))
    return np.nan

def assign_service_type(row:pd.Series):
    producto = str(row['Conceptos ClaveProdServ SAT Descripción'])
    descripcion = str(row['Conceptos Descripción']).upper()
    rfc_emisor = str(row['Emisor RFC'])
    ref_ext_sap = str(row['Ref. externa SAP']).upper()
    proveedor = str(row['ID Proveedor SAP'])
    serv = row['Servicio']

    if 'Instituciones bancarias' in producto:
        # si el concepto es instituciones bancarias, se cataloga como comisiones o intereses bancarios,
        # dependiendo del texto de la descripción
        if re.match(r'COMISI[ÓO]+N', descripcion):
            return 'Comisiones bancarias'
        elif re.match(r'INTER[EÉ]+S', descripcion):
            return 'Intereses bancarios'
        else: return 'Comisiones bancarias'
    elif 'Servicios de transferencia de fondos y canje y cambios' in producto:
        return 'Compra de divisas'
    elif 'Seguros de asistencia médica y hospitalización' in producto \
        or ('Servicios de seguros para estructuras y propiedades y posesiones' in producto and not re.match(r'T[\d]{4,5}', proveedor)):
        return 'Seguros y fianzas'
    elif rfc_emisor=='IMS421231I45':
        return 'IMSS'
    elif rfc_emisor=='PUN9810229R0':
        return 'SI VALE'
    elif 'Transporte de pasajeros aérea' in producto \
        or 'Viajes en aviones comerciales' in producto:
        return 'Aerolíneas'
    elif '-AE-' in ref_ext_sap:
        return 'AE'
    elif '-AI-' in ref_ext_sap:
        return 'AI'
    elif '-MI-' in ref_ext_sap:
        return 'MI'
    elif '-ME-' in ref_ext_sap:
        return 'ME'
    elif not serv is np.nan or re.match(r'T[\d]{4,5}', proveedor):
        return 'Terrestre'
    elif re.match(r'G[\d]{4,5}', proveedor):
        return 'Gasto'
    elif proveedor!='No identificado':
        return 'Acreedores'
    else: return 'No identificado'

def format_request_url(base_url : str, report_name : str, parameters: dict):
    """Devuelve URL de consulta OData con el formato correcto"""

    select_str =  "$select=" + ','.join(parameters['select'])

    if len(parameters['filter'])>0:
        filter_str = f"$filter=({parameters['filter'][0]})"
        # Si hay más de un filtro, los une mediante un 'and'
        if len(parameters['filter'])>1:
            for i in range(1,len(parameters['filter'])):
                filter_str+= f" and ({parameters['filter'][i]})"
    else:
        filter_str=''
    
    if filter_str=='':
        url = base_url+report_name+'QueryResults?'+select_str+'&$format=json'
    else:
        url = base_url+report_name+'QueryResults?'+select_str+'&'+filter_str+'&$format=json'

    return url

def request_df(base_url : str, report_name : str, parameters : dict, username : str, password : str):
    "Realiza petición OData y regresa los resultados en un Dataframe"

    headers = {"Accept": "application/json"}  # ensure JSON is returned
    # Make the request
    url = format_request_url(base_url, report_name, parameters)
    # print(f"Requesting URL: {url}")
    response = requests.get(url, auth=(username, password), headers=headers)
    print(f"Response: {response}")
    # print("DETAILS: "
    #       f"URL: {response.url}, Status Code: {response.status_code}, Reason: {response.reason}")
    if response.status_code == 200:
    # Generate Dataframe
        try:
            df = pd.json_normalize(response.json()['d']['results'])
            # CPOSTING_DATE from string ms to datetime
            if 'CPOSTING_DATE' in df.columns:
                df['CPOSTING_DATE'] = pd.to_datetime(df['CPOSTING_DATE'].str.extract(r'/Date\((\d+)\)/')[0].astype(int), unit='ms')
            if 'CTRANSDAT' in df.columns:
                df['CTRANSDAT'] = pd.to_datetime(df['CTRANSDAT'].str.extract(r'/Date\((\d+)\)/')[0].astype(int), unit='ms')
            return df
        except Exception as error:
            print(error)
            return None
    else:
        print("Error Response Text:", response.text)  # safer than .json() for 401
        return None

def get_provs(rfc_list:list, bucket_size: int = 30)->pd.DataFrame:
    """Obtiene los proveedores de SAP a partir de una lista de RFCs"""
    report_name = "RPBUPSPP_Q0001"
    parameters = {
        'select': ['CBP_UUID', 'CTAX_ID_NR','CCREATION_DT','C1QITSQE6F9TSX3J3DUJRLUJGY5'],
    }
    # realizamos la petición en buckets de 30 RFCs
    provs = pd.DataFrame()
    for i in range(0, len(rfc_list), bucket_size):
        print(f'[Procesando RFCs {i+1} a {min(i+bucket_size, len(rfc_list))} de {len(rfc_list)}]')
        rfc_bucket = rfc_list[i:i+bucket_size]
        filter_rfc = " or ".join([f"CTAX_ID_NR eq '{rfc}'" for rfc in rfc_bucket])
        parameters['filter'] = [filter_rfc]
        provs_bucket = request_df(st.secrets['sap_odata_base_url'], report_name, parameters, st.secrets['sap_username'], st.secrets['sap_password'])
        if provs_bucket is not None:
            print(f'[Proveedores obtenidos en este bucket: {len(provs_bucket)}]')
            provs = pd.concat([provs, provs_bucket], ignore_index=True)
    # depuramos la fecha de creación
    provs['CCREATION_DT'] = pd.to_datetime(provs['CCREATION_DT'].str.split(' ').str[0], errors='raise', format='%d.%m.%Y')
    # ordenamos descendentemente por ID de proveedor y fecha de creación
    provs = provs.sort_values(['CBP_UUID','CCREATION_DT'], ascending=[False, False])
    # # ordenamos descendentemente por fecha de creación
    # provs = provs.sort_values('CCREATION_DT', ascending=False)
    # quitamos duplicados por RFC, dejando la primera (la de fecha más reciente)
    provs = provs.drop_duplicates(subset=['CTAX_ID_NR'], keep='first').reset_index(drop=True)
    provs.rename(columns={'CBP_UUID':'ID Proveedor SAP', 'CTAX_ID_NR':'RFC Proveedor', 'CCREATION_DT':'Fecha creación proveedor', 'C1QITSQE6F9TSX3J3DUJRLUJGY5':'Ejecutivo CPP SAP'}, inplace=True)
    print(f'Proveedores obtenidos: {len(provs)}')
    return provs

def excel_col_letter(col_idx):
    """Convierte índice de columna (0-based) a letra de Excel (A, B, ..., Z, AA, AB, ...)"""
    letters = ''
    while col_idx >= 0:
        letters = chr(col_idx % 26 + 65) + letters
        col_idx = col_idx // 26 - 1
    return letters

def is_numeric(df:pd.DataFrame,col:str):
    """Verifica si una columna de un DataFrame es numérica."""
    return pd.api.types.is_numeric_dtype(df[col])

# Dynamic table functionality

def dynamic_table(
    df: pd.DataFrame,
    rows: list[str],
    cols: list[str],
    values: dict[str, str],  # {column: aggfunc}
    filters: dict[str, list],
    name: str,
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

    # --- Filtering widgets ---
    filtered_df = df.copy()
    for col, preselected in filters.items():
        unique_vals = df[col].dropna().unique().tolist()
        if preselected:
            preselected = [val for val in preselected if val in unique_vals]# correct preselected to make sure the value exists
        ms_key = f"ms_{name}_{col.replace(' ','_')}"
        if st.session_state.get(ms_key) is None:
            selected = st.multiselect(
                f"{col}",
                options=unique_vals,
                default=preselected,
                # generate a unique key using the name and column name
                key=ms_key
            )
            st.session_state[ms_key] = selected
        else:
            selected = st.session_state[ms_key]
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
    # 

    # --- Display ---
    st.table(pivot_df, border='horizontal')