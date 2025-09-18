import pandas as pd

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