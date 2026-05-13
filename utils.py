import re
import numpy as np
import pandas as pd
import requests
import streamlit as st
import urllib.parse
import os
import tomli
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config import COLS_SERVICE, ENV_FILE_PATH, CATALOGO_SERV_PROD

def clean_dtypes(df: pd.DataFrame, num_cols: list[str], date_cols: list[str], date_format=None):
    """Corrección de los tipos de datos, según la lista de columnas numéricas o de fecha."""
    # obtenemos las columnas que tienen tipo numérico pero no están en num_cols
    other_num_cols = [col for col in df.select_dtypes(include=['number']).columns if col not in num_cols + date_cols]
    
    # en num_cols, extraemos los caracteres que corresponden a números y reemplazamos NaN por 0
    for col in num_cols:
        df[col] = df[col].astype(str).fillna('0').str.extract(r'([\d,\.]+)')[0].str.replace(',', '').astype(float)
    # las que no son num_cols ni date_cols, reemplazamos NaN por cadena vacía
    df = df.fillna({col: '' for col in df.columns if col not in num_cols + date_cols})
    
    # transformamos a numérico las columnas en num_cols
    # df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='raise')
    # obtenemos el valor absoluto para evitar negativos en numéricas
    df[num_cols] = df[num_cols].abs()
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
    pattern = rf'(2[123456]+)[ ]?[- _‐]+[ ]?(\d{{4,6}})'
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
    # si no se ha identificado, se usa el catálogo de productos
    for serv,prods in CATALOGO_SERV_PROD.items():
        for prod in prods:
            if prod in producto: return serv
    # si no está en el catálogo, se pone como 'No identificado'
    return 'No identificado'

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
    response = requests.get(url, auth=(username, password), headers=headers)
    print(f"Response: {response}")
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

def get_provs(rfc_list:list,username,password, bucket_size: int = 30)->pd.DataFrame:
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
        provs_bucket = request_df(st.secrets['sap_odata_base_url'], report_name, parameters, username, password)
        if provs_bucket is not None:
            print(f'[Proveedores obtenidos en este bucket: {len(provs_bucket)}]')
            provs = pd.concat([provs, provs_bucket], ignore_index=True)
    if provs.empty:
        print('No se obtuvieron proveedores de SAP.')
        return None
    # depuramos la fecha de creación
    provs['CCREATION_DT'] = pd.to_datetime(provs['CCREATION_DT'].str.split(' ').str[0], errors='raise', format='%d.%m.%Y')
    # ordenamos descendentemente por ID de proveedor y fecha de creación
    provs = provs.sort_values(['CBP_UUID','CCREATION_DT'], ascending=[False, False])
    # quitamos duplicados por RFC, dejando la primera (la de fecha más reciente)
    provs = provs.drop_duplicates(subset=['CTAX_ID_NR'], keep='first').reset_index(drop=True)
    provs.rename(columns={'CBP_UUID':'ID Proveedor SAP', 'CTAX_ID_NR':'RFC Proveedor', 'CCREATION_DT':'Fecha creación proveedor', 'C1QITSQE6F9TSX3J3DUJRLUJGY5':'Ejecutivo CPP SAP'}, inplace=True)
    print(f'Proveedores obtenidos: {len(provs)}')
    return provs

# Funciones para acceso a base de datos SQL Server
def load_env_vars(file_path: str)->dict:
    """Loads enviroment variables from a .env file"""
    with open(file_path, "r", encoding='utf-8') as env_file:
        env_vars = {}
        for line in env_file:
            key, value = line.strip().split("=", 1)
            env_vars[key.strip()] = value.strip()
    if not all(k in env_vars for k in ['server', 'user', 'password', 'table_provs']):
        raise ValueError("Missing required environment variables in the .env file.")
    print(env_vars)
    return env_vars

def execute_query(engine: Engine, query: str)->pd.DataFrame:
    """Executes a SQL query and returns the result as a DataFrame"""
    return pd.read_sql(query, engine)

def connect_to_db(env_vars:dict)->Engine:
    """Creates a SQLAlchemy engine using the provided environment variables"""
    odbc_str = (
        "DRIVER={SQL Server};"
        f"SERVER={env_vars['server']};"
        f"UID={env_vars['user']};"
        f"PWD={env_vars['password']};"
    )
    connection_string = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc_str)
    return create_engine(connection_string)

def get_provs_from_dwh(rfc_list:list)->pd.DataFrame:
    """Main function to get providers from the DWH based on a list of RFCs"""
    env_vars = load_env_vars(ENV_FILE_PATH)
    engine = connect_to_db(env_vars)
    table = env_vars['table_provs']
    rfc_tuple = tuple(rfc_list)
    query = f"""SELECT Proveedor, [Número de identificación fiscal], [Ejecutivo de Cuentas por Pagar] FROM {table} WHERE [Número de identificación fiscal] IN {rfc_tuple} ORDER BY Proveedor DESC;"""
    provs = execute_query(engine, query)
    if provs.empty:
        print('No se obtuvieron proveedores de SAP.')
        return None
    provs.rename(columns={
        'Número de identificación fiscal': 'RFC Proveedor',
        'Proveedor': 'ID Proveedor SAP',
        'Ejecutivo de Cuentas por Pagar': 'Ejecutivo CPP SAP'
    }, inplace=True)
    # ordenamos descendentemente por ID de proveedor
    provs = provs.sort_values(by='ID Proveedor SAP', ascending=False)
    # quitamos duplicados por RFC, dejando la primera ocurrencia
    provs = provs.drop_duplicates(subset='RFC Proveedor', keep='first')
    return provs

def get_fact_sap_from_dwh(period:tuple[str])->pd.DataFrame:
    env_vars = load_env_vars(ENV_FILE_PATH)
    engine = connect_to_db(env_vars)
    table = env_vars['table_saldos']
    query = f"SELECT * FROM {table} WHERE [Fecha de factura] LIKE'{date_range_to_regex(period)}'"
    return execute_query(engine, query)

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
def multiselect_key(name: str, col: str) -> str:
    """Genera una clave única para el multiselect de un filtro en la tabla dinámica."""
    return f"ms_{name}_{col.replace(' ','_')}"

def update_filters(filters:dict, name:str):
    """Actualiza los filtros de la tabla dinámica según las selecciones del usuario en Streamlit."""
    updated_filters = {}
    for col, values in filters.items():
        if values is None:
            updated_filters[col] = None
        else:
            key = multiselect_key(name, col)
            if st.session_state.get(key) is not None:
                selected_values = st.session_state[key]
            else:
                selected_values = values
            if len(selected_values) == 0:
                updated_filters[col] = None
            else:
                updated_filters[col] = selected_values
    return updated_filters

def get_multiselect_values(name:str, default_filters:dict):
    """Obtiene los valores seleccionados en los multiselects de los filtros de la tabla dinámica."""
    selected_values = {}
    for col in default_filters.keys():
        key = multiselect_key(name, col)
        if st.session_state.get(key) is not None:
            selected_values[col] = st.session_state[key]
        else:
            selected_values[col] = default_filters[col]
    return selected_values

def assign_ejecutivo_cxp(fact_sat: pd.DataFrame) -> pd.DataFrame:
    """Asigna el ejecutivo de CxP a las facturas basándose en datos históricos y SAP.
    
    Args:
        fact_sat (pd.DataFrame): DataFrame con las facturas, debe contener 'Emisor RFC', 'Moneda', 'Creado por', 'Ejecutivo CPP SAP'.
    
    Returns:
        pd.DataFrame: DataFrame con la columna 'Ejecutivo CxP' asignada.
    """
    try:
        env_vars = load_env_vars(ENV_FILE_PATH)
        ejecutivos_file = env_vars['ejecutivos_file']
        with open(ejecutivos_file, 'rb') as f:
            data = tomli.load(f)
        # Asumir que el archivo .toml tiene una sección 'ejecutivos' con una lista de entradas
        ejecutivos_cxp = pd.DataFrame(data.get('ejecutivos_cxp', []))
        print(ejecutivos_cxp.head())
    except Exception as e:
        print(f'Advertencia: no se pudo cargar el archivo de ejecutivos {env_vars.get("ejecutivos_file", "desconocido")}: {e}. Se usará solo información disponible.')
        ejecutivos_cxp = pd.DataFrame(columns=['rfc', 'moneda', 'ejecutivo_cxp'])

    fact_sat = fact_sat.merge(
        ejecutivos_cxp,
        left_on=['Emisor RFC', 'Moneda'],
        right_on=['rfc', 'moneda'],
        how='left'
    )
    if 'ejecutivo_cxp' in fact_sat.columns:
        fact_sat['Ejecutivo CxP'] = fact_sat['Creado por'] \
            .fillna(fact_sat['ejecutivo_cxp']) \
            .fillna(fact_sat['Ejecutivo CPP SAP']) \
            .fillna('No identificado')
    else:
        fact_sat['Ejecutivo CxP'] = fact_sat['Creado por'] \
            .fillna(fact_sat['Ejecutivo CPP SAP']) \
            .fillna('No identificado')
    
    return fact_sat

def get_most_recent_file(folder_path: str, extension: str) -> str:
    """Obtiene la ruta del archivo más reciente en la carpeta con la extensión dada.
    
    Args:
        folder_path (str): Ruta de la carpeta a buscar.
        extension (str): Extensión del archivo (ej. '.txt', 'txt').
    
    Returns:
        str or None: Ruta completa del archivo más reciente, o None si no se encuentra.
    """
    if not os.path.exists(folder_path):
        print(f"❌ La carpeta {folder_path} no existe.")
        return None
    
    files = [f for f in os.listdir(folder_path) if f.endswith(extension)]
    if not files:
        print(f"❌ No se encontraron archivos con extensión '{extension}' en {folder_path}.")
        return None
    
    # Obtener el archivo con la fecha de modificación más reciente
    most_recent = max(files, key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
    return os.path.join(folder_path, most_recent)

def date_range_to_regex(period:tuple[str], separator = '.')->str:
    """Transforms a date range ('dd-mm-yyyy','dd-mm-yyyy') into a regular expression that matches
    string dates of the form 'dd[]mm[]yyyy' within the range, where [] stands for the separator"""
    return "%.2026"