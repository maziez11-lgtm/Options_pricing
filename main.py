"""TTF natural gas options pricing — demo script.

Example market parameters:
    F  = 35 EUR/MWh  (TTF front-month forward)
    K  = 35 EUR/MWh  (at-the-money)
    T  = 0.25 years  (3-month expiry)
    r  = 0.03        (3% risk-free rate)
"""

from pricing import black76, bachelier, greeks, implied_vol


def demo_black76() -> None:
    F, K, T, r, sigma = 35.0, 35.0, 0.25, 0.03, 0.50

    call = black76.call_price(F, K, T, r, sigma)
    put = black76.put_price(F, K, T, r, sigma)

    print("=== Black-76 (TTF futures option) ===")
    print(f"  Call : {call:.4f} EUR/MWh")
    print(f"  Put  : {put:.4f} EUR/MWh")

    g = greeks.b76_greeks(F, K, T, r, sigma, "call")
    print("  Greeks (call):")
    for name, val in g.items():
        print(f"    {name:<8}: {val:.6f}")

    # Round-trip implied vol
    iv = implied_vol.solve(call, F, K, T, r, option_type="call", model="black76")
    print(f"  Implied vol (Black-76): {iv:.6f}  (input: {sigma})")


def demo_bachelier() -> None:
    # Negative-price scenario (gas crisis inversion)
    F, K, T, r, sigma_n = -5.0, 0.0, 0.25, 0.03, 8.0  # sigma_n in EUR/MWh

    call = bachelier.call_price(F, K, T, r, sigma_n)
    put = bachelier.put_price(F, K, T, r, sigma_n)

    print("\n=== Bachelier (negative price scenario) ===")
    print(f"  F = {F} EUR/MWh, K = {K} EUR/MWh, sigma_n = {sigma_n} EUR/MWh")
    print(f"  Call : {call:.4f} EUR/MWh")
    print(f"  Put  : {put:.4f} EUR/MWh")

    g = greeks.bach_greeks(F, K, T, r, sigma_n, "call")
    print("  Greeks (call):")
    for name, val in g.items():
        print(f"    {name:<8}: {val:.6f}")

    iv = implied_vol.solve(call, F, K, T, r, option_type="call", model="bachelier")
    print(f"  Implied normal vol (Bachelier): {iv:.6f} EUR/MWh  (input: {sigma_n})")


def demo_put_call_parity() -> None:
    """Verify put-call parity: C - P = DF * (F - K)."""
    F, K, T, r, sigma = 40.0, 38.0, 0.5, 0.03, 0.45
    call = black76.call_price(F, K, T, r, sigma)
    put = black76.put_price(F, K, T, r, sigma)
    import math
    parity_lhs = call - put
    parity_rhs = math.exp(-r * T) * (F - K)
    print("\n=== Put-Call Parity Check ===")
    print(f"  C - P        = {parity_lhs:.6f}")
    print(f"  DF * (F - K) = {parity_rhs:.6f}")
    print(f"  Difference   = {abs(parity_lhs - parity_rhs):.2e}")


if __name__ == "__main__":
    demo_black76()
    demo_bachelier()
    demo_put_call_parity()
