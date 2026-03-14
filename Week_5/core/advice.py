"""
advice.py
---------
Generates human-readable recommendations.
Uses templates to avoid unsafe or vague outputs.
"""

def generate_advice(state, goal):
    if state == "Recovery Needed":
        return (
            "Your body shows signs of fatigue. "
            "Prioritize sleep, hydration, and light movement today."
        )

    if state == "Overloaded":
        return (
            "Training stress is high with limited recovery. "
            "Reduce intensity and focus on mobility or stretching."
        )

    if state == "Underactive":
        return (
            "Activity levels are low. "
            "A short walk or light workout will help maintain consistency."
        )

    if state == "Optimal":
        if goal == "fat_loss":
            return (
                "Your routine is balanced. "
                "Maintain consistency and a moderate calorie deficit."
            )
        if goal == "muscle_gain":
            return (
                "Recovery and load are well balanced. "
                "Continue progressive overload with adequate nutrition."
            )

    return "Maintain healthy habits and listen to your body."
