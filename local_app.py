# se ejecuta este script para realizar la conciliación en un entorno local en lugar de streamlit cloud
# todos los parámetros necesarios están en el archivo .env, la ruta debe especificarse en config.py

import logging
from config import EXPECTED_COLS, DATE_FORMATS_BY_REPORT, DEFAULT_DATE_FORMAT, ENV_FILE_PATH, PERIOD
from conc import conciliar_local
from clean_data import read_excel_file, process_dataframe
from utils import get_provs_from_dwh, load_env_vars, get_most_recent_file, get_fact_sap_from_dwh
from datetime import datetime
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# primeramente, validamos que se puedan obtener los proveedores desde SAP con las credenciales guardadas en el archivo .env
env_vars = load_env_vars(ENV_FILE_PATH)
test_provs = get_provs_from_dwh(['XAXX010101000','XEXX010101000'])
if test_provs is None:
    logger.error('Error al obtener datos de proveedores desde SAP. Verifica tus credenciales y conexión a la base de datos.')
else:
    logger.info('Conexión a SAP exitosa.')
    # validamos que env_vars contenga los paths a los archivos de facturas SAT, SAP, Box y complementos de pago, así como output_path para guardar resultados
    missing_paths = [key for key in ['fact_sat_path', 'box_path', 'cp_path', 'output_path', 'table_provs', 'table_saldos'] if key not in env_vars]
    if len(missing_paths) > 0:
        logger.error(f'Faltan las siguientes rutas de archivos en el archivo .env: {missing_paths}')
    else:
        logger.info('Rutas de archivos cargadas desde .env correctamente. Procediendo a leer los archivos...')
        # leemos los archivos de facturas SAT, SAP, Box y complementos de pago usando la función read_excel_file
        # se toma el archivo más reciente dentro de la carpeta correspondiente
        logger.info('Leyendo reporte de facturas SAT...')
        fact_sat = read_excel_file(
            get_most_recent_file(env_vars['fact_sat_path'],'.xlsx'),
            session_name='fact_sat',
            expected_columns=EXPECTED_COLS['fact_sat'],
            header=4,
            date_format=DATE_FORMATS_BY_REPORT.get('fact_sat', DEFAULT_DATE_FORMAT)
        )
        logger.info('Leyendo reporte de Box...')
        box = read_excel_file(
            get_most_recent_file(env_vars['box_path'],'.xlsx', name_contains='Reporte_CFDI'),
            session_name='box',
            expected_columns=EXPECTED_COLS['box'],
            date_format=DATE_FORMATS_BY_REPORT.get('box', DEFAULT_DATE_FORMAT)
        )
        logger.info('Leyendo reporte de CP SAT...')
        cp = read_excel_file(
            get_most_recent_file(env_vars['cp_path'],'.xlsx'),
            session_name='cp',
            expected_columns=EXPECTED_COLS['cp'],
            header=4,
            date_format=DATE_FORMATS_BY_REPORT.get('cp', DEFAULT_DATE_FORMAT)
        )
        # para las facturas de SAP, se consulta la DB directamente
        logger.info('Consultando reporte de Saldos de Proveedor...')
        fact_sap = get_fact_sap_from_dwh(PERIOD).rename(columns={'Creado por2':'Creado por'})
        fact_sap = process_dataframe(fact_sap, session_name='fact_sap',
                                     expected_columns=EXPECTED_COLS['fact_sap'],
                                     date_formats={'fact_sap':'%Y-%m-%d'})
        logger.info('Reporte de saldos procesado.')

        reportes = {'fact_sat': fact_sat, 'fact_sap': fact_sap, 'box': box, 'cp': cp}
        reportes_fallidos = [nombre for nombre, df in reportes.items() if df is None]
        if reportes_fallidos:
            logger.error(
                f'No se pudo continuar: fallaron los siguientes reportes: {reportes_fallidos}. '
                'Revisa los mensajes de error anteriores para más detalle de cada archivo.'
            )
        else:
            logger.info('Archivos leídos correctamente. Procediendo a conciliación...')
            timestamp = datetime.now().strftime('%y-%m-%d %H %M')
            conciliacion = conciliar_local(fact_sat, fact_sap, box, cp, env_vars['output_path']+rf"\conc_fact_rec {timestamp}.xlsx")
            logger.info(f'Conciliación completada: {len(conciliacion)} filas generadas.')