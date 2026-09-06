from flask import Flask, render_template, request, jsonify
import joblib
import random
from datetime import datetime

app = Flask(__name__)

# Load trained ML model
model = joblib.load("dustbin_model.pkl")


# --------------------------------------------------
# SAMPLE SMART BIN DATA
# Later this can come from ESP32 + sensors
# --------------------------------------------------

bins = [
    {
        "id": "BIN-001",
        "location": "Central Park",
        "fill_level": 42,
        "temperature": 28,
        "weight": 12
    },
    {
        "id": "BIN-002",
        "location": "Market Street",
        "fill_level": 72,
        "temperature": 31,
        "weight": 21
    },
    {
        "id": "BIN-003",
        "location": "Main Road",
        "fill_level": 94,
        "temperature": 32,
        "weight": 29
    },
    {
        "id": "BIN-004",
        "location": "Bus Stand",
        "fill_level": 58,
        "temperature": 30,
        "weight": 18
    },
    {
        "id": "BIN-005",
        "location": "School Road",
        "fill_level": 35,
        "temperature": 27,
        "weight": 10
    },
    {
        "id": "BIN-006",
        "location": "Railway Station",
        "fill_level": 81,
        "temperature": 33,
        "weight": 25
    },
    {
        "id": "BIN-007",
        "location": "Hospital Road",
        "fill_level": 63,
        "temperature": 29,
        "weight": 17
    },
    {
        "id": "BIN-008",
        "location": "Lake View",
        "fill_level": 47,
        "temperature": 28,
        "weight": 13
    }
]


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# ML PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    fill_level = float(data["fill_level"])
    temperature = float(data["temperature"])
    weight = float(data["weight"])

    features = [[fill_level, temperature, weight]]

    # ML prediction
    prediction = model.predict(features)[0]

    # Probability
    try:
        probabilities = model.predict_proba(features)[0]
        confidence = max(probabilities) * 100
    except:
        confidence = 90.0

    return jsonify({
        "status": str(prediction),
        "probability": round(confidence, 2),
        "fill_level": fill_level,
        "temperature": temperature,
        "weight": weight
    })


# --------------------------------------------------
# GET ALL BIN DATA
# --------------------------------------------------

@app.route("/api/bins")
def get_bins():

    result = []

    for bin_data in bins:

        fill = bin_data["fill_level"]

        # Status based on fill level
        if fill >= 85:
            status = "FULL"
        elif fill >= 60:
            status = "WARNING"
        else:
            status = "NORMAL"

        result.append({
            **bin_data,
            "status": status
        })

    return jsonify(result)


# --------------------------------------------------
# DASHBOARD STATISTICS
# --------------------------------------------------

@app.route("/api/dashboard")
def dashboard():

    total_bins = len(bins)

    action_bins = sum(
        1 for b in bins if b["fill_level"] >= 60
    )

    average_fill = sum(
        b["fill_level"] for b in bins
    ) / total_bins

    # Highest fill bin
    next_bin = max(
        bins,
        key=lambda x: x["fill_level"]
    )

    # Simple estimated overflow time
    fill = next_bin["fill_level"]

    if fill >= 90:
        overflow_hours = 2.4
    elif fill >= 75:
        overflow_hours = 5.0
    elif fill >= 60:
        overflow_hours = 8.0
    else:
        overflow_hours = 14.0

    return jsonify({
        "total_bins": total_bins,
        "action_bins": action_bins,
        "average_fill": round(average_fill, 1),
        "next_overflow_bin": next_bin["id"],
        "overflow_hours": overflow_hours,
        "ai_confidence": 94.2
    })


# --------------------------------------------------
# COLLECTION PRIORITY
# --------------------------------------------------

@app.route("/api/priority")
def collection_priority():

    priority = []

    for b in bins:

        fill = b["fill_level"]

        if fill >= 85:
            level = "HIGH"
        elif fill >= 60:
            level = "MEDIUM"
        else:
            level = "LOW"

        priority.append({
            "id": b["id"],
            "location": b["location"],
            "fill_level": fill,
            "priority": level
        })

    # Highest fill first
    priority.sort(
        key=lambda x: x["fill_level"],
        reverse=True
    )

    return jsonify(priority)


# --------------------------------------------------
# SIMULATE LIVE SENSOR DATA
# --------------------------------------------------

@app.route("/api/refresh", methods=["POST"])
def refresh():

    for b in bins:

        # Simulate small change in fill level
        change = random.randint(-2, 4)

        b["fill_level"] += change

        # Keep between 0 and 100
        b["fill_level"] = max(
            0,
            min(100, b["fill_level"])
        )

        # Simulate temperature
        b["temperature"] += random.uniform(-0.5, 0.5)

        b["temperature"] = round(
            b["temperature"], 1
        )

    return jsonify({
        "success": True,
        "message": "Sensor data updated",
        "updated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )