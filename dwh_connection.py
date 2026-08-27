import logging
import pandas as pd
import re
from sqlalchemy import create_engine, Engine
from urllib.parse import quote_plus
from config import ENV_FILE_PATH

logger = logging.getLogger(__name__)

def load_env_vars(file_path: str)->dict:
    """Loads environment variables from a .env file using UTF-8 encoding."""
    with open(file_path, "r", encoding="utf-8-sig") as env_file:
        env_vars = {}
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip()
    if not all(k in env_vars for k in ['server', 'user', 'password',]):
        raise ValueError("Missing required environment variables in the .env file.")
    # No se registran los valores: incluyen credenciales sensibles (usuario, password, etc.)
    logger.debug(f'Variables de entorno cargadas desde "{file_path}": {list(env_vars.keys())}')
    return env_vars


def connect_to_db(env_vars:dict)->Engine:
    """Creates a SQLAlchemy engine using the provided environment variables"""
    odbc_str = (
        "DRIVER={SQL Server};"
        f"SERVER={env_vars['server']};"
        f"UID={env_vars['user']};"
        f"PWD={env_vars['password']};"
        f"DATABASE={env_vars['database']}"
    )
    connection_string = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_str)
    return create_engine(connection_string)

def format_sql_value(value):
        """Formats common Python dtypes to fit a SQL query string."""
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (list, tuple)):
            items = ",".join(format_sql_value(item) for item in value)
            return f"({items})"
        if isinstance(value, str):
            if value.upper() in {"NULL", "TRUE", "FALSE"}:
                return value.upper()
            if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                return value
            if value.startswith("(") and value.endswith(")"):
                return value
            return "'" + value.replace("'", "''") + "'"
        return "'" + str(value).replace("'", "''") + "'"

def repl_vars(query: str, vars: dict[str, str] = None)->str:
    """Takes in a SQL query and sets the variables according to the vars dictionary.
    If a variable is already assigned inside the query, its SET statement is replaced.
    If not, a SET statement is inserted after the DECLARE clause.
    Variables not declared in the query are ignored and reported.
    """
    if not vars:
        return query
    
    updated_query = query

    for var_name, value in vars.items():
        key = var_name if var_name.startswith("@") else f"@{var_name}"
        literal = format_sql_value(value)

        decl_pattern = re.compile(rf"(?i)\bDECLARE\s+{re.escape(key)}\b[^;]*;", re.MULTILINE)
        set_pattern = re.compile(rf"(?i)\bSET\s+{re.escape(key)}\s*=\s*.*?;", re.MULTILINE)

        if set_pattern.search(updated_query):
            updated_query = set_pattern.sub(lambda _: f"SET {key} = {literal};", updated_query, count=1)
        elif decl_pattern.search(updated_query):
            updated_query = decl_pattern.sub(
                lambda match: f"{match.group(0)}\nSET {key} = {literal};",
                updated_query,
                count=1,
            )
        else:
            logger.warning(f'Variable {key} no encontrada en la consulta; se omite.')

    return updated_query



def execute_query(query: str, vars: dict[str, str] = None, label: str = None)->pd.DataFrame:
    """Connects to the database and executes a SQL query, returning the result as a DataFrame
    If the vars dictionary is not None, it assigns the corresponding values to their variables
    (when already declared within the query)."""
    env_vars = load_env_vars(ENV_FILE_PATH)
    engine = connect_to_db(env_vars)
    query = repl_vars(query, vars)
    logger.info(f'Ejecutando consulta{f": {label}" if label else ""}')
    return pd.read_sql(query, engine)


def execute_query_from_path(path: str, vars: dict[str, str] = None)->pd.DataFrame:
    """Connects to the database and executes the query contained in a .sql file.
    If the vars dictionary is not None, it assigns the corresponding values to their variables
    (when already declared within the query).
    Returns the result as a DataFrame."""
    # read file
    try:
        with open(path, "r", encoding="utf-8") as sql_file:
            query = sql_file.read()
    except OSError as e:
        logger.error(f'No se pudo leer el archivo de consulta "{path}": {e}')
        raise
    return execute_query(query, vars, label=path)
