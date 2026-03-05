"""
rules.py
--------
This file contains decision-making logic.
Rules override models for safety and clarity.
"""

def health_state(signals):
    """
    Determines the user's overall health state.
    """

    # Burnout & safety first
    if signals["stress"] == "High" or signals["sleep_debt"] == "Severe":
        return "Recovery Needed"

    # Overtraining detection
    if signals["recovery"] == "Under-recovered" and signals["load"] > 300:
        return "Overloaded"

    # Low activity detection
    if signals["load"] < 100:
        return "Underactive"

    # Default healthy state
    return "Optimal"
