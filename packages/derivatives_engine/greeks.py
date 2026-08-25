"""
Market AI — Black-Scholes Pricing & Option Greeks Engine
Computes analytical Black-Scholes option pricing and first/second order Greeks:
Delta, Gamma, Theta, Vega, and Implied Volatility (IV).
"""

import math
from typing import Dict, Any, Optional
from scipy.stats import norm


class BlackScholesGreeks:
    """Calculates Black-Scholes European option pricing and Greeks."""

    @staticmethod
    def calculate_greeks(
        spot: float,
        strike: float,
        time_to_expiry_years: float,
        volatility: float,  # annualized volatility (e.g. 0.16 for 16%)
        risk_free_rate: float = 0.065,  # RBI 91-day T-bill rate ~6.5%
        option_type: str = "CE",  # "CE" for Call, "PE" for Put
    ) -> Dict[str, float]:
        """Calculates exact analytical Greeks."""
        if time_to_expiry_years <= 0:
            time_to_expiry_years = 0.0001
        if volatility <= 0:
            volatility = 0.01

        S = float(spot)
        K = float(strike)
        T = float(time_to_expiry_years)
        r = float(risk_free_rate)
        sigma = float(volatility)

        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        pdf_d1 = norm.pdf(d1)
        cdf_d1 = norm.cdf(d1)
        cdf_d2 = norm.cdf(d2)
        cdf_neg_d1 = norm.cdf(-d1)
        cdf_neg_d2 = norm.cdf(-d2)

        # Gamma (identical for Call & Put)
        gamma = pdf_d1 / (S * sigma * math.sqrt(T))

        # Vega (identical for Call & Put, per 1% change in IV)
        vega = (S * pdf_d1 * math.sqrt(T)) / 100.0

        if option_type.upper() in ["CE", "CALL"]:
            # Call Premium
            price = S * cdf_d1 - K * math.exp(-r * T) * cdf_d2
            delta = cdf_d1
            # Theta (per 1 calendar day decay)
            theta = (
                -(S * pdf_d1 * sigma) / (2.0 * math.sqrt(T))
                - r * K * math.exp(-r * T) * cdf_d2
            ) / 365.0
        else:
            # Put Premium
            price = K * math.exp(-r * T) * cdf_neg_d2 - S * cdf_neg_d1
            delta = cdf_d1 - 1.0
            # Theta (per 1 calendar day decay)
            theta = (
                -(S * pdf_d1 * sigma) / (2.0 * math.sqrt(T))
                + r * K * math.exp(-r * T) * cdf_neg_d2
            ) / 365.0

        return {
            "price": round(max(0.05, float(price)), 2),
            "delta": round(float(delta), 4),
            "gamma": round(float(gamma), 6),
            "theta": round(float(theta), 2),
            "vega": round(float(vega), 2),
            "iv": round(sigma * 100.0, 2),
        }
