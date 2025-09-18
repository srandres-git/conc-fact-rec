import pandas as pd
import numpy as np
import streamlit as st


def conciliar(fact_sat: pd.DataFrame, fact_sap: pd.DataFrame, box: pd.DataFrame, cp: pd.DataFrame):
    with st.session_state['conc']:
        st.write('Conciliado')
        st.write(fact_sat)
        st.write(fact_sap)
        st.write(box)
        st.write(cp)