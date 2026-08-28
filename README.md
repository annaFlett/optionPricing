# Options Pricing Interactive Visulisation

After learning about options pricing and modelling the stock market, I created a number of interactive tools to further solidify my understanding and allow myself to explore the effect changing variables has on pricing.

## Black Scholes Page
I created an interactive calculator for the Black Scholes model designed to let me investigate how the model reacts to changes in each of the variables. The sliders allow the user to vary parameters, which are then used to calculate the price of call and put options and the values of the Greeks. These calculated values are then displayed in the table at the top.

The chart section allows the user to hold all variables constant except one to explore how that variable affects pricing in isolation. The user can select which variable to vary using the drop-down menu (volatility, expiration date and underlying's price). Two graphs, one displaying option price vs quantity being varied and the other displaying the value of a Greek vs the quantity being varied (the Greek can be selected by the user using the drop-down menu), are displayed. An example of these graphs can be seen below. The sliders can be used to change which value the other variables are held constant at. 

![](https://github.com/annaFlett/optionPricing/blob/main/images/blackscholes.png "Black Scholes Page")

## Monte Carlo Page

On this page, I use Geometric Brownian Motion to model the movement of stock price. From this simulation I calculate the Monte Carlo price and compare the resulting P/L with the Black-Scholes model. I provide the option to simulate the stock price under risk-neutral measure or real-world measure. The parameters for the simulation can be changed using the sliders to investigate the impact each of them has on the price path.

Below I then explore the convergence of Monte Carlo price as a function of the number of simulations used to calculate it. The convergence behaviour can be investigated for different values of μ. When μ = r, the simulated stock follows the risk-neutral dynamics used in Black-Scholes pricing and the Monte Carlo estimate converges to this price. When μ ≠ r, the Monte Carlo estimate converges to a different value because the simulation is based on the real-world measure rather than the risk-neutral measure.

![](https://github.com/annaFlett/optionPricing/blob/main/images/montecarlo.png "Monte Carlo Page")
