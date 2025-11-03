import pandas as pd
import streamlit as st
from utils import clean_dtypes, sort_df
from config import NUM_COLS_FACT_SAT, DATE_COLS_FACT_SAT, \
    NUM_COLS_FACT_SAP, DATE_COLS_FACT_SAP, DATE_COLS_BOX, \
    NUM_COLS_CP, DATE_COLS_CP, \
    MONTH_MAP_ENG_ESP, CLEANING_FUNCTIONS


def depurar_sat(fact_sat: pd.DataFrame)->pd.DataFrame:
    # la coulmna de 'UUID' a mayúsculas
    fact_sat['UUID'] = fact_sat['UUID'].str.upper()
    fact_sat['CFDI Relacionado'] = fact_sat['CFDI Relacionado'].str.upper()
    fact_sat['UUID Sustitución'] = fact_sat['UUID Sustitución'].str.upper()
    # solo facturas sin UUID vacío
    fact_sat = fact_sat[(fact_sat['UUID'].str.strip() != '')
                        & (~fact_sat['UUID'].isna())
                        & (fact_sat['UUID'].str.strip() != '0')]

    # limpiamos los tipos de datos de fact_sat
    fact_sat = clean_dtypes(fact_sat, NUM_COLS_FACT_SAT, DATE_COLS_FACT_SAT)

    # tipo de cambio a 1 si la moneda es MXN
    fact_sat.loc[fact_sat['Moneda'] == 'MXN', 'Tipo Cambio'] = 1
    # si el tipo de cambio es 0 o NaN, lo ponemos a 1
    fact_sat.loc[fact_sat['Tipo Cambio'].isna() | (fact_sat['Tipo Cambio'] == 0), 'Tipo Cambio'] = 1

    # agregamos la columna de Mes según la fecha de emisión en formato 'MMM'
    fact_sat['Mes'] = fact_sat['Emisión'].dt.strftime('%b')
    # mapeamos los nombres de meses en español
    fact_sat['Mes'] = fact_sat['Mes'].map(MONTH_MAP_ENG_ESP)

    rename_cols_fact_sat = {
        'Total': 'Total SAT MXN',
        'Total Original XML': 'Total SAT XML',
    }
    fact_sat = fact_sat.rename(columns=rename_cols_fact_sat)
    
    return fact_sat

def depurar_sap(fact_sap: pd.DataFrame)-> pd.DataFrame:
    # limpiamos los tipos de datos de fact_sap
    fact_sap = clean_dtypes(fact_sap, NUM_COLS_FACT_SAP, DATE_COLS_FACT_SAP,)

    # ID de factura oficial y UUID corregido a mayúsculas
    fact_sap['ID de factura oficial'] = fact_sap['ID de factura oficial'].str.upper()
    fact_sap['UUID Corregido'] = fact_sap['UUID Corregido'].str.upper()

    # Ordenamos por estado de factura: 'Pagado', 'Parcialmente pagado','Contabilizada','Cancelada' 
    status_order = ['Pagado', 'Parcialmente pagado', 'Contabilizada', 'Cancelada']
    fact_sap = sort_df(fact_sap, 'Estado de factura', status_order, drop_dup_col='UUID Corregido')

    return fact_sap

def depurar_box(box: pd.DataFrame)-> pd.DataFrame:
    # limpiamos los tipos de datos de box
    box = clean_dtypes(box, num_cols=[], date_cols=DATE_COLS_BOX)
    # UUID a mayúsculas
    box['UUID'] = box['UUID'].str.upper()

    # aquellas con patrón de ruta de archivo 
    # "[más caracteres]\Box\Facturas Multilog\["Pesos" o "Dolares"]\[nombre de carpeta de proveedor]\[nombre de archivo][fin de la cadena]"
    # se les cambia el estatus a 'RAIZ'
    root_pattern = r".*\\Box\\Facturas Multilog\\(Pesos|Dolares)\\[^\\]+\\[^\\]+$"
    box.loc[box['Ruta_Archivo'].str.match(root_pattern, na=False), 'Estatus'] = 'RAIZ'
    # los que tengas estatus vacío, se les pone 'SIN ESTATUS'
    box.loc[box['Estatus'].str.strip() == '', 'Estatus'] = 'SIN ESTATUS'

    # Ordenamos por estatus
    status_order_box = ['OK','PAGADAS', 'PENDIENTES','RAIZ', 'CANCELADAS', 'CARTA PORTE', 'COMPLEMENTOS DE PAGO', 'NOTAS DE CRÉDITO', 'COMPLEMENTARIAS','SIN ESTATUS']
    box = sort_df(box, 'Estatus', status_order_box, drop_dup_col='UUID')

    return box

def depurar_cp(cp: pd.DataFrame)-> pd.DataFrame:
    # UUID  y UUIDRel a mayúsculas
    cp['UUID'] = cp['UUID'].str.upper()
    cp['UUIDRel'] = cp['UUIDRel'].str.upper()
    # solo pagos con UUID no vacío
    cp = cp[(cp['UUID'].str.strip() != '')
            & (cp['UUID'].str.strip() != '0')
            & (cp['UUID'].notna())
        ].reset_index(drop=True)

    # limpiamos los tipos de datos de cp
    cp = clean_dtypes(cp, NUM_COLS_CP, DATE_COLS_CP, date_format = '%d/%m/%Y')

    # tipos de cambio a 1 si es cero o NaN
    cp.loc[cp['TipoCambioDR'].isna() | (cp['TipoCambioDR'] == 0), 'TipoCambioDR'] = 1
    cp.loc[cp['TipoCambioP'].isna() | (cp['TipoCambioP'] == 0), 'TipoCambioP'] = 1

    # Ordenamos por estatus
    status_order_cp = ['Vigente', 'Cancelado']
    cp = sort_df(cp, 'Estatus', status_order_cp, drop_dup_col='UUIDRel')

    return cp

# file reader functionality
def read_excel_file(file, session_name:str, expected_columns:list, header:int=0)->pd.DataFrame:
    """Lee un archivo Excel validando que contenga las columnas esperadas y asigna a session state."""
    try:
        df = pd.read_excel(file, header=header)
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if len(missing_cols) > 0:
            st.error(f'El archivo cargado no contiene las columnas esperadas: {missing_cols}', icon="❌")
            return None
        else:
            # depuramos el DataFrame según la función correspondiente (si existe)
            cleaning_function_name = CLEANING_FUNCTIONS.get(session_name, None)
            if cleaning_function_name:
                cleaning_function = globals()[cleaning_function_name]
                df = cleaning_function(df)
            # st.session_state[session_name] = df
            st.success('Archivo leído correctamente.', icon="✅")
            return df
    except Exception as e:
        st.error(f'Error al leer el archivo: {e}', icon="❌")
        return None