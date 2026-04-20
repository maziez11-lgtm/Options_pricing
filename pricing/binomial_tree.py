"""Cox-Ross-Rubinstein binomial tree for American and European options."""

import math
import numpy as np


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    steps: int = 200,
    option_type: str = "call",
    style: str = "american",
) -> float:
    """Price an option using the CRR binomial tree.

    Args:
        S: Current spot price
        K: Strike price
        T: Time to expiry in years
        r: Risk-free rate (annualised)
        sigma: Volatility (annualised)
        steps: Number of time steps
        option_type: 'call' or 'put'
        style: 'american' or 'european'
    """
    dt = T / steps
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    discount = math.exp(-r * dt)
    p = (math.exp(r * dt) - d) / (u - d)  # risk-neutral up-probability

    # Terminal asset prices
    prices = S * d ** np.arange(steps, -1, -1) * u ** np.arange(0, steps + 1)

    # Terminal payoffs
    if option_type == "call":
        values = np.maximum(prices - K, 0.0)
    else:
        values = np.maximum(K - prices, 0.0)

    # Backward induction
    for i in range(steps - 1, -1, -1):
        values = discount * (p * values[1:] + (1 - p) * values[:-1])
        if style == "american":
            asset = S * d ** np.arange(i, -1, -1) * u ** np.arange(0, i + 1)
            if option_type == "call":
                values = np.maximum(values, asset - K)
            else:
                values = np.maximum(values, K - asset)

    return float(values[0])
