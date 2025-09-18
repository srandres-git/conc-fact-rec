import pandas as pd
import numpy as np
import streamlit as st
from config import RENAME_COLS_SAP, EJECUTIVO_SAP_MAP

def sat_x_sap(fact_sat: pd.DataFrame, fact_sap: pd.DataFrame)->pd.DataFrame:
    """Cruce de facturas de SAT vs SAP. Ambos reportes iniciales depurados."""

    fact_sat = fact_sat.merge(fact_sap[['UUID Corregido','Estado de factura','Referencia externa','Creado por','Importe de la factura']], left_on='UUID', right_on='UUID Corregido', how='left', suffixes=('', '_sap'))
    fact_sat.rename(columns=RENAME_COLS_SAP, inplace=True)
    fact_sat.replace({'Creado por': EJECUTIVO_SAP_MAP}, inplace=True)

    # los NaN en 'UUID Corregido', 'Estado de factura', 'Referencia externa' se ponen como "No está SAP"
    fact_sat['UUID SAP'] = fact_sat['UUID SAP'].fillna('No está SAP')
    fact_sat['Estatus SAP'] = fact_sat['Estatus SAP'].fillna('No está SAP')
    fact_sat['Ref. externa SAP'] = fact_sat['Ref. externa SAP'].fillna('No está SAP')
    # los NaN en 'Importe de la factura' se ponen como 0
    fact_sat['Total SAP XML'] = fact_sat['Total SAP XML'].fillna(0)
    # calculamos Total SAP MXN
    fact_sat['Total SAP MXN'] = fact_sat['Total SAP XML'] * fact_sat['Tipo Cambio']
    # diferencias entre SAT y SAP, MXN y XML
    fact_sat['Dif. Total MXN'] = (fact_sat['Total SAT MXN'] - fact_sat['Total SAP MXN']).abs()
    fact_sat['Dif. Total XML'] = (fact_sat['Total SAT XML'] - fact_sat['Total SAP XML']).abs()

    return fact_sat



def sat_x_box(fact_sat: pd.DataFrame, box: pd.DataFrame)->pd.DataFrame:
    """Cruce de facturas de SAT vs Box. Ambos reportes iniciales previamente depurados."""
    # extraemos los RFC de las facturas de Box
    rfcs_box = box['Emisor_RFC'].str.upper().str.strip().unique()

    # cruzamos Box con fact_sat
    fact_sat = fact_sat.merge(box[['UUID','Estatus','Ruta_Archivo']], left_on='UUID', right_on='UUID', how='left', suffixes=('', ' Box'))
    fact_sat.rename(columns={'Ruta_Archivo': 'Ruta Box'}, inplace=True)

    # separamos los que están en Box y los que no
    fact_sat_in_box = fact_sat[fact_sat['Estatus Box'].notna()].copy()
    fact_sat_not_in_box = fact_sat[fact_sat['Estatus Box'].isna()].copy()

    # de los que no están en Box, verificamos si el RFC del emisor está en los RFCS de Box
    # si es así, se les pone 'No está Box'; si no, se les pone 'No buscado en Box'
    fact_sat_not_in_box['Estatus Box'] = np.where(
        fact_sat_not_in_box['Emisor RFC'].str.upper().str.strip().isin(rfcs_box),
        'No está Box',
        'No buscado en Box'
    )
    # unimos los dos dataframes
    fact_sat = pd.concat([fact_sat_in_box, fact_sat_not_in_box], ignore_index=True)
    # Aignamos los mismos valores en 'Ruta Box' para los documentos no encontrados en Box
    fact_sat['Ruta Box'] = fact_sat['Ruta Box'].fillna(fact_sat['Estatus Box'])

    return fact_sat

def sat_x_cp(fact_sat: pd.DataFrame, cp: pd.DataFrame)->pd.DataFrame:
    """Cruce de facturas de SAT vs complementos de pago. Ambos reportes iniciales previamente depurados."""
    # hacemos merge con cp para obtener estatus de pagos
    fact_sat = fact_sat.merge(cp[['UUIDRel','Estatus']], left_on='UUID', right_on='UUIDRel', how='left', suffixes=('', ' CP'))
    # rellenamos los NaN en 'Estatus CP' con 'Sin CP'
    fact_sat['Estatus CP'] = fact_sat['Estatus CP'].fillna('Sin CP')

    return fact_sat


def conciliar(fact_sat: pd.DataFrame, fact_sap: pd.DataFrame, box: pd.DataFrame, cp: pd.DataFrame):
    # Realizamos los cruces de los reportes base
    fact_sat = sat_x_sap(fact_sat,fact_sap)
    fact_sat = sat_x_box(fact_sat, box)
    fact_sat = sat_x_cp(fact_sat, cp)

    with st.session_state['conc']:
        st.write(fact_sat)