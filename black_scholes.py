import numpy as np
import streamlit as st
from scipy.stats import norm
import pandas as pd
import altair as alt

st.set_page_config(page_title="Black-Scholes",layout='wide')

rng = np.random.default_rng(42)
CALL_COLOUR = "#7ABAF5"
PUT_COLOUR = "#FCB54E"
GREEK_MAP = {'Delta' : 1, 'Gamma' : 2, 'Theta' : 3, 'Vega' : 4, 'Rho' : 5}

class Option():
    """Class to define an Option. Expiration should be given in days"""
    def __init__(self,strike,expiration,type):
        self.strike = strike
        self.expiration = expiration
        self.type = type

def calculate_black_scholes_price(option,sigma,S,r):
    """ Using the Black Scholes model to calculate the risk-neutral price of an option (specified as call or put)
     K = Option's strike price
     t = Years to option's expiration
     S = Underlying asset's current price
     sigma = Volatility of the market
     r = Risk-free interest rate
     Formulas for the price + the greeks : https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model#Black%E2%80%93Scholes_formula"""
    K = option.strike
    t = option.expiration / 365
    d1 = (np.log(S/K) + (r + sigma**2 / 2) * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)
    call_price = S*norm.cdf(d1) - K * np.exp(-r*t)*norm.cdf(d2)
    put_price = K*np.exp(-r*t) * norm.cdf(-d2) - S*norm.cdf(-d1)

    # Vega and gamma are the same regardless of if the option is a put or call
    vega = S*norm.pdf(d1) * np.sqrt(t)
    gamma = norm.pdf(d1) / (S*sigma*(np.sqrt(t)))
    if option.type == "Call":
        delta = norm.cdf(d1)
        rho = K * t *np.exp(-r*t)*norm.cdf(d2)
        theta = -(S*norm.pdf(d1)*sigma) / (2*np.sqrt(t)) - r*K*np.exp(-r*t)*norm.cdf(d2)
        return [call_price,delta,gamma,theta,vega,rho]
            
    elif option.type == "Put":
        delta = -norm.cdf(-d1)
        rho = - K * t *norm.cdf(-d2)
        theta = - (S*norm.pdf(d1)*sigma) / (2*np.sqrt(t)) + r*K*np.exp(-r*t)*norm.cdf(-d2)
        return [put_price,delta,gamma,theta,vega,rho]

# Web-app utilities
def make_chart(x_vals,varying,f_opt,f_greek):
    df = pd.DataFrame({varying: x_vals, 'Option Price (Call)': f_opt(x_vals,"Call"),"Option Price (Put)": f_opt(x_vals,"Put"),
                        f"{greek_display} (Call)" : f_greek(x_vals,"Call"),f"{greek_display} (Put)" : f_greek(x_vals,"Put"), 'Strike' : [K] * len(x_vals)})
    base = alt.Chart(df).encode(x=alt.X(varying,scale=alt.Scale(reverse=varying == "Expiration Date"))).properties(height=400)
    line1 = base.mark_line(color=CALL_COLOUR).encode(y=alt.Y(f'Option Price (Call)',title="Option Price"))
    line2 = base.mark_line(color=PUT_COLOUR).encode(y='Option Price (Put)')
    option_chart = line1 + line2
    if varying == "Underlying Price":    
        line3 = base.mark_rule(color='green',strokeDash = [5,5]).encode(x="Strike")
        option_chart += line3
    line4 = base.mark_line(color=CALL_COLOUR).encode(y=alt.Y(f'{greek_display} (Call)',title=greek_display))
    line5 = base.mark_line(color=PUT_COLOUR).encode(y=f'{greek_display} (Put)')
    greek_chart = line4 + line5

    return (option_chart, greek_chart)

def highlight_rows(row):
    colours = {'Call Option': f'background-color: {CALL_COLOUR}',
        'Put Option': f'background-color: {PUT_COLOUR}'}
    return [colours[row.name]] * len(row)

def gen_charts():
    if quantity_to_vary == "Underlying Price":
        x_vals = np.arange(1,250)
        f_opt = lambda x,y : calculate_black_scholes_price(Option(K,days_to_expiry,y),sigma,x,r)[0]
        f_greek = lambda x,y : calculate_black_scholes_price(Option(K,days_to_expiry,y),sigma,x,r)[GREEK_MAP[greek_display]]
    elif quantity_to_vary == "Volatility":
        x_vals = np.arange(0.01,2,0.01)
        f_opt = lambda x,y : calculate_black_scholes_price(Option(K,days_to_expiry,y),x,S,r)[0]
        f_greek = lambda x,y : calculate_black_scholes_price(Option(K,days_to_expiry,y),x,S,r)[GREEK_MAP[greek_display]]
    elif quantity_to_vary == "Expiration Date":
        x_vals = np.arange(1,1096)
        f_opt = lambda x,y : calculate_black_scholes_price(Option(K,x,y),sigma,S,r)[0]
        f_greek = lambda x,y : calculate_black_scholes_price(Option(K,x,y),sigma,S,r)[GREEK_MAP[greek_display]]
    return make_chart(x_vals, quantity_to_vary, f_opt,f_greek)

# Sidebar config
st.sidebar.header("Parameters")
S = st.sidebar.slider("Underlying Asset Price", min_value=1,value=100,max_value=200)
r = st.sidebar.slider("Risk-Free Rate", min_value=0.0, value=0.05,max_value=1.0)
K = st.sidebar.slider("Strike Price",min_value=1,value=100,max_value=200)
days_to_expiry = st.sidebar.slider("Days to Expiry", min_value=1, value=365,max_value=1095)
sigma = st.sidebar.slider("Volatility", min_value=0.01, value=0.1,max_value=2.0)

st.sidebar.header("Chart")
greek_display = st.sidebar.selectbox("Display Greek", ['Delta','Gamma','Theta','Vega','Rho'])
quantity_to_vary = st.sidebar.selectbox("Vary",["Underlying Price", "Volatility", "Expiration Date"])

# Option pricing table
values_df = pd.DataFrame([calculate_black_scholes_price(Option(K,days_to_expiry,x),sigma,S,r) for x in ['Call','Put']],
        columns=['Price','Delta','Gamma','Theta','Vega','Rho'],
        index=['Call Option','Put Option'])

styled_df = (values_df.style.apply(highlight_rows, axis=1).set_table_styles([
        {'selector': 'th.col_heading',
        'props': [('background-color', 'grey'),('color', 'white')]},
        {'selector': 'th.row_heading',
         'props': [('background-color', 'grey'),('color', 'white')]}]))
st.table(styled_df)

# Chart display
opt_table, greek_table = gen_charts()
st.altair_chart(opt_table,width='stretch')
st.altair_chart(greek_table,width='stretch')