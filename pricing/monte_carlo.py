"""Monte Carlo simulation for option pricing."""

import math
import numpy as np


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    simulations: int = 100_000,
    option_type: str = "call",
    seed: int | None = None,
) -> tuple[float, float]:
    """Price a European option via Monte Carlo simulation.

    Returns:
        (price, standard_error)
    """
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(simulations)
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * Z)

    if option_type == "call":
        payoffs = np.maximum(ST - K, 0.0)
    else:
        payoffs = np.maximum(K - ST, 0.0)

    discounted = math.exp(-r * T) * payoffs
    price_est = float(discounted.mean())
    std_err = float(discounted.std() / math.sqrt(simulations))
    return price_est, std_err


def price_asian(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    steps: int = 252,
    simulations: int = 50_000,
    option_type: str = "call",
    averaging: str = "arithmetic",
    seed: int | None = None,
) -> tuple[float, float]:
    """Price an Asian (average-price) option.

    Args:
        averaging: 'arithmetic' or 'geometric'
    Returns:
        (price, standard_error)
    """
    rng = np.random.default_rng(seed)
    dt = T / steps
    Z = rng.standard_normal((simulations, steps))
    increments = (r - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * Z
    log_prices = np.log(S) + np.cumsum(increments, axis=1)
    paths = np.exp(log_prices)  # shape: (simulations, steps)

    if averaging == "arithmetic":
        avg = paths.mean(axis=1)
    else:
        avg = np.exp(np.log(paths).mean(axis=1))

    if option_type == "call":
        payoffs = np.maximum(avg - K, 0.0)
    else:
        payoffs = np.maximum(K - avg, 0.0)

    discounted = math.exp(-r * T) * payoffs
    price_est = float(discounted.mean())
    std_err = float(discounted.std() / math.sqrt(simulations))
    return price_est, std_err
