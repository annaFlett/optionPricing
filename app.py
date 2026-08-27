import streamlit as st

st.set_page_config(page_title="Black-Scholes",layout='wide')

black_scholes = st.Page("black_scholes.py", title = "Black Scholes")
monte_carlo = st.Page("monteCarlo.py", title="Monte Carlo")
pg = st.navigation([black_scholes, monte_carlo],position='top')
pg.run()
