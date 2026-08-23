import numpy as np
import matplotlib.pyplot as plt

# Assumption of risk neutrality, price of the option is the expected discounted payoff
# Based on model given by https://intro.quantecon.org/monte_carlo.html
# Stock price at time t, St, modelled by => ln S_t+1 = ln S_t + mu + sigma_t * zeta_t+1
# Stochastic volatility model
rng = np.random.default_rng(42)

def price_path(s0,mu,rho,nu,h0,T):
    s_t = np.log(s0)
    predictions = []
    h_t = h0
    for _ in range(1,T+1):
        sigma_t = np.exp(h_t)
        s_t = s_t + mu + sigma_t * rng.standard_normal()
        h_t = rho * h_t + nu *  rng.standard_normal()
        predictions.append(np.exp(s_t))
    return predictions

# Setting values
default_μ  = 0.0001
default_ρ  = 0.1
default_ν  = 0.001
default_S0 = 10
default_h0 = 0
default_K = 100
default_n = 10
default_β = 0.95
default_knockout = 120
default_M = 100000

# Calculating option price using Monte Carlo 
payoffs = np.array([max(price_path(default_S0,default_μ,default_ρ,default_ν,default_h0,default_n)[-1] - default_K,0) for _ in range(0,default_M)])
price = default_β**default_n * np.mean(payoffs)
print(f"Option Price = {price}")

# Same, but using options with a knockout barrier
payoffs = np.empty(default_M)
for i in range(0,default_M):
    j = np.array(price_path(default_S0,default_μ,default_ρ,default_ν,default_h0,default_n))
    if i < 8:
        plt.plot(np.arange(1,default_n+1),j)
    if (j >= default_knockout).any():
        payoffs[i] = 0
    else:
        payoffs[i] = max(j[-1] - default_K,0)

price = default_β**default_n * np.mean(payoffs)
print(f"Option Price = {price}")
plt.show()