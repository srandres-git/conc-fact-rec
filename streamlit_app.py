import streamlit as st

pg_conc = st.Page('pg_conc.py', title="Generar conciliación", icon="🧾")
pg_dashboard = st.Page('pg_dashboard.py', title="Dashboard", icon="📊")

pg = st.navigation([pg_conc, pg_dashboard])
st.set_page_config(page_title='Conciliación de facturas recibidas', layout='wide', page_icon='🧾')
pg.run()