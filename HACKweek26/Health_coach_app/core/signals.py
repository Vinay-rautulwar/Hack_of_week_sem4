"""
signals.py
-----------
This file converts raw health data into interpretable signals.
Signals are simplified indicators used by the rule engine.
"""

def activity_load(workout_minutes, intensity):
    """
    Measures physical stress from workouts.
    """
    return workout_minutes * intensity


def sleep_debt(sleep_hours):
    """
    Calculates sleep deficit based on ideal sleep.
    """
    ideal_sleep = 7.5
    debt = max(0, ideal_sleep - sleep_hours)

    if debt == 0:
        return "None"
    elif debt <= 1:
        return "Mild"
    else:
        return "Severe"


def recovery_state(sleep_hours, load):
    """
    Estimates recovery capacity using sleep and training load.
    """
    if sleep_hours < 6 and load > 300:
        return "Under-recovered"
    elif sleep_hours >= 7:
        return "Recovered"
    else:
        return "Neutral"


def stress_state(stress_level):
    """
    Converts self-reported stress into categories.
    """
    if stress_level <= 2:
        return "Low"
    elif stress_level <= 4:
        return "Moderate"
    else:
        return "High"
