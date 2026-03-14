from flask import Flask, render_template, request

from core.signals import (
    activity_load,
    sleep_debt,
    recovery_state,
    stress_state
)
from core.rules import health_state
from core.advice import generate_advice
from database.db import init_db, insert_health_data

app = Flask(__name__)

# Initialize database and tables at application startup
init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        # Read form inputs
        sleep_hours = float(request.form["sleep"])
        workout_minutes = int(request.form["minutes"])
        workout_intensity = int(request.form["intensity"])
        stress_level = int(request.form["stress"])
        goal = request.form["goal"]

        # Store data in SQLite database
        insert_health_data({
            "sleep_hours": sleep_hours,
            "workout_minutes": workout_minutes,
            "workout_intensity": workout_intensity,
            "stress_level": stress_level,
            "goal": goal
        })

        # Compute health signals
        load = activity_load(workout_minutes, workout_intensity)

        signals = {
            "load": load,
            "sleep_debt": sleep_debt(sleep_hours),
            "recovery": recovery_state(sleep_hours, load),
            "stress": stress_state(stress_level)
        }

        # Determine health state and generate advice
        state = health_state(signals)
        advice = generate_advice(state, goal)

        result = {
            "signals": signals,
            "state": state,
            "advice": advice
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
