# se ejecuta este script para realizar la conciliación en un entorno local en lugar de streamlit cloud
# todos los parámetros necesarios están en el archivo .env, la ruta debe especificarse en config.py

from config import EXPECTED_COLS, ENV_FILE_PATH, PERIOD
from conc import conciliar_local
from clean_data import read_excel_file, process_dataframe
from utils import get_provs_from_dwh, load_env_vars, get_most_recent_file, get_fact_sap_from_dwh
from datetime import datetime

# primeramente, validamos que se puedan obtener los proveedores desde SAP con las credenciales guardadas en el archivo .env
env_vars = load_env_vars(ENV_FILE_PATH)
test_provs = get_provs_from_dwh(['XAXX010101000','XEXX010101000'])
if test_provs is None:
    print('❌ Error al obtener datos de proveedores desde SAP. Verifica tus credenciales y conexión a la base de datos.')
else:
    print('✅ Conexión a SAP exitosa.')
    # validamos que env_vars contenga los paths a los archivos de facturas SAT, SAP, Box y complementos de pago, así como output_path para guardar resultados
    missing_paths = [key for key in ['fact_sat_path', 'box_path', 'cp_path', 'output_path', 'table_provs', 'table_saldos'] if key not in env_vars]
    if len(missing_paths) > 0:
        print(f'❌Faltan las siguientes rutas de archivos en el archivo .env: {missing_paths}')
    else:
        print('✅ Rutas de archivos cargadas desde .env correctamente. Procediendo a leer los archivos...')
        # leemos los archivos de facturas SAT, SAP, Box y complementos de pago usando la función read_excel_file
        # se toma el archivo más reciente dentro de la carpeta correspondiente
        print('... Leyendo reporte de facturas SAT')
        fact_sat = read_excel_file(get_most_recent_file(env_vars['fact_sat_path'],'.xlsx'), session_name='fact_sat', expected_columns=EXPECTED_COLS['fact_sat'], header=4)        
        print('... Leyendo reporte de Box')
        box = read_excel_file(get_most_recent_file(env_vars['box_path'],'.xlsx'), session_name='box', expected_columns=EXPECTED_COLS['box'])
        print('... Leyendo reporte de CP SAT')
        cp = read_excel_file(get_most_recent_file(env_vars['cp_path'],'.xlsx'), session_name='cp', expected_columns=EXPECTED_COLS['cp'], header=4)
        # para las facturas de SAP, se consulta la DB directamente
        print('... Consultando reporte de Saldos de Proveedor')
        fact_sap = get_fact_sap_from_dwh(PERIOD).rename(columns={'Creado por2':'Creado por'})
        fact_sap = process_dataframe(fact_sap, session_name='fact_sap', expected_columns=EXPECTED_COLS['fact_sap'])
        print('✅ Reporte de saldos procesado.')
        if any(df is None for df in [fact_sat,fact_sap,box,cp]):
            print('❌ Error al leer uno o más archivos. Verifica que los archivos existan y tengan las columnas esperadas.')
        else:
            print('✅ Archivos leídos correctamente. Procediendo a conciliación...')
            timestamp = datetime.now().strftime('%y-%m-%d %H %M')
            conciliacion = conciliar_local(fact_sat, fact_sap, box, cp, env_vars['output_path']+rf"\conc_fact_rec {timestamp}.xlsx")
            print('✅ Conciliación completada. Resultados:')
            print(conciliacion.head())