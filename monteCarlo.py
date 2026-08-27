import numpy as np
import streamlit as st
from scipy.stats import norm
import pandas as pd
import altair as alt
from black_scholes import calculate_black_scholes_price, Option

st.set_page_config(page_title="Black-Scholes",layout='wide')
rng = np.random.default_rng()

# Modelling functions
def price_path_gbm(S0,mu,sigma,T,dt):
    """Uses a Geometric Brownian Motion model to realise a random path for a stock's price
    s0 = intial stock price
    mu = annual drift / expected rate of return
    sigma = annualised volatility of underlying's returns
    T = no of days to simulation
    dt = no of days distance between each simulated price"""
    predictions = [S0]
    s_t = S0
    dt_in_years = dt/365
    for _ in np.arange(0,T,dt):
        s_t = s_t * np.exp(dt_in_years*(mu - 0.5 * sigma**2) + sigma * rng.normal(scale=np.sqrt(dt_in_years)))
        predictions.append(s_t)
    return predictions

def final_price_gbm(S0,mu,sigma,T,size=1):
    """Calculate the price at time T (in years), according to Geometric Brownian Motion"""
    T = T / 365
    return S0 * np.exp((mu - sigma**2/2)*T + sigma * rng.normal(scale=np.sqrt(T),size=size))

def calc_payoff(option_type,final_price,K):
    """Calculate the payoff of an option, given the final price of the underlying"""
    if option_type == "Call":
        return np.maximum(final_price - K,0)
    else:
        return np.maximum(K - final_price,0)

# Streamlit utilities
def generate_path(risk_neutral=True):
    """Generate a new price path (risk_neutral)"""
    if risk_neutral:
        st.session_state.path = price_path_gbm(S, r, sigma, days_to_expiry, 1)
    else:
        st.session_state.path = price_path_gbm(S, mu, sigma, days_to_expiry, 1)
    st.session_state.path_params = (S, sigma, days_to_expiry,r,mu,risk_neutral)

    
def generate_convergence_graph():
    """Generate a new convergence graph"""
    prices = []
    sim_num = np.arange(1,MAX_SIM,10000)
    all_price_samples = final_price_gbm(S,mu,sigma,days_to_expiry,size=300000)
    for M in sim_num:
        payoffs = calc_payoff(option_type,all_price_samples[0:M],K)
        prices.append(np.exp(-r*(days_to_expiry/365)) * np.mean(payoffs))

    st.session_state.comp_df = pd.DataFrame({"Number of Simulations" : sim_num,
                            "Black Scholes" : [calculate_black_scholes_price(Option(K,days_to_expiry,option_type),sigma,S,r)[0]] * len(sim_num),
                            "Monte Carlo Price" : prices})

def highlight_rows(row):
    """Colour P/L green if > 0, and red otherwise"""
    colour = "transparent"
    if row.name in ['Black Scholes P/L','Monte Carlo P/L']:
        colour = "green" if row['Premium Price (per share)'] > 0 else "red"
    return [f"background-color: {colour}"] * len(row)

# Sidebar config
st.sidebar.header("Parameters")
S = st.sidebar.slider("Underlying Asset Price", min_value=1,value=100,max_value=200)
K = st.sidebar.slider("Strike Price",min_value=1,value=100,max_value=200)
days_to_expiry = st.sidebar.slider("Days to Expiry", min_value=1, value=365,max_value=1095)
mu = st.sidebar.slider("Annual Expected Return / Drift", min_value=0.0, value=0.05,max_value=1.0)
r = st.sidebar.slider("Risk-Free Rate", min_value=0.0, value=0.05,max_value=1.0)
sigma = st.sidebar.slider("Volatility", min_value=0.01, value=0.1,max_value=2.0)
M = st.sidebar.slider("Number of simulations (MC P/L)",  min_value=1, value=1000,max_value=100000)
option_type = st.sidebar.selectbox("Option Type", ['Call','Put'])
MAX_SIM = 301001

# Handles intial graph generation
path_params = (S, sigma, days_to_expiry,r,mu,True)

if "path" not in st.session_state:
    generate_path()
    st.session_state.path_params = path_params

if "comp_df" not in st.session_state:
    generate_convergence_graph()
    st.session_state.path_params = path_params

col1, col2 = st.columns([7,2])

sim_under = col2.radio(label="Path simulated under:",options=['Risk-neutral measure (r)', 'Real-world measure (mu)'])
risk_neutral = sim_under == 'Risk-neutral measure (r)'

# Handles graph regeration when parameters change
path_params = (S, sigma, days_to_expiry,r,mu,risk_neutral)

if st.session_state.path_params != path_params:
    generate_path(risk_neutral=risk_neutral)
    generate_convergence_graph()
    path_params = st.session_state.path_params

# Calculation of Black Scholes and Monte Carlo Premium Prices
price_path = st.session_state.path
final_price = price_path[-1]
option_payoff = calc_payoff(option_type,final_price,K)

premium_bs = calculate_black_scholes_price(Option(K,days_to_expiry,option_type),sigma,S,r)[0]
pnl_bs = option_payoff - premium_bs

final_prices_mc = final_price_gbm(S,r,sigma,days_to_expiry,size=M)
payoffs_mc = calc_payoff(option_type,final_prices_mc,K)
premium_mc = np.exp(-r*(days_to_expiry/365)) * np.mean(payoffs_mc)
prices_df = pd.DataFrame({'Premium Price (per share)' : [premium_bs,pnl_bs,premium_mc,option_payoff - premium_mc] },index=['Black Scholes','Black Scholes P/L','Monte Carlo','Monte Carlo P/L'])


# Values table
styled_df = (prices_df.style.apply(highlight_rows, axis=1).set_table_styles([
        {'selector': 'th.col_heading',
        'props': [('background-color', 'grey'),('color', 'white')]},
        {'selector': 'th.row_heading',
         'props': [('background-color', 'grey'),('color', 'white')]}]))
col2.table(styled_df)
col2.write("Note : Monte Carlo price is always calculated under risk-neutral pricing")
if col2.button("Generate new path"):
    generate_path(risk_neutral=risk_neutral)

# First graph
df = pd.DataFrame({"Days": np.arange(0,days_to_expiry+1), 'Predicted Price': price_path, 'Strike' : [K] * (1+days_to_expiry)})
base = alt.Chart(df).encode(x=alt.X("Days",scale=alt.Scale(domain=[0,days_to_expiry + 5]))).properties(height=400)
line1 = base.mark_line().encode(y="Predicted Price")
line2 = base.mark_line(color="green").encode(y=alt.Y("Strike", scale=alt.Scale(zero=False)))
col1.altair_chart(line1 + line2,width='stretch')

# Second graph
col3, col4 = st.columns([7,2])
base = alt.Chart(st.session_state.comp_df).encode(x=alt.X("Number of Simulations",scale=alt.Scale(domain=[0, MAX_SIM + 1000])))
line3 = base.mark_line(color='orange').encode(y="Black Scholes")
line4 = base.mark_line(color="pink").encode(y=alt.Y("Monte Carlo Price", scale=alt.Scale(zero=False), title="Premium Price (per share)"))
legend_df = pd.DataFrame({"Series": ["Black Scholes Price", "Monte Carlo Price"],"x": [0, 0],"y": [0, 0]})
legend = alt.Chart(legend_df).mark_point(opacity=0).encode(color=alt.Color("Series", scale=alt.Scale(domain=["Black Scholes", "Monte Carlo"], range=["orange", "pink"]),title=None))

col3.altair_chart(line3 + line4 + legend,width='stretch')
col4.write("This graph shows how the Monte Carlo Price converges to a value as the number of simulations are increased.")
col4.write("When simulating using r = μ, it can be seen that the Monte Carlo Price converges to the Black Scholes price. " \
"When r != μ, the Monte Carlo price coverges to a different value to Black-Scholes. " \
"This is because Black-Scholes prices options under a risk-neutral measure, so for the Monte Carlo " \
"price to converge to it, it needs to be derived from an underlying simulated under risk-neutral conditions.")
col4.button(label="Regenerate graph", on_click=generate_convergence_graph)
