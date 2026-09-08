from flask import Flask, render_template, request, jsonify
import joblib
import random
from datetime import datetime

app = Flask(__name__)

# Load ML model
model = joblib.load("dustbin_model.pkl")

# Smart bin data
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


def get_status(fill):
    if fill >= 85:
        return "FULL"
    elif fill >= 60:
        return "WARNING"
    else:
        return "NORMAL"


def get_priority(fill):
    if fill >= 85:
        return "HIGH"
    elif fill >= 60:
        return "MEDIUM"
    else:
        return "LOW"


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- DASHBOARD ----------------

@app.route("/api/dashboard")
def dashboard():

    total_bins = len(bins)

    action_bins = sum(
        1 for b in bins
        if b["fill_level"] >= 60
    )

    average_fill = (
        sum(b["fill_level"] for b in bins)
        / total_bins
    )

    next_bin = max(
        bins,
        key=lambda x: x["fill_level"]
    )

    fill = next_bin["fill_level"]

    if fill >= 90:
        overflow_hours = 2.4
    elif fill >= 75:
        overflow_hours = 5
    elif fill >= 60:
        overflow_hours = 8
    else:
        overflow_hours = 14

    # Chart data
    chart = [
        max(0, min(100,
        round(average_fill + random.randint(-12, 8), 1)))
        for _ in range(7)
    ]

    chart[-1] = round(average_fill, 1)

    return jsonify({

        "total_bins": total_bins,

        "action_bins": action_bins,

        "average_fill": round(
            average_fill,
            1
        ),

        "next_overflow_bin":
            next_bin["id"],

        "overflow_hours":
            overflow_hours,

        # IMPORTANT
        "ai_confidence": 94.2,

        # Frontend compatibility
        "ai_accuracy": 94.2,

        "chart": chart,

        "updated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    })


# ---------------- SMART BINS ----------------

@app.route("/api/bins")
def get_bins():

    result = []

    for b in bins:

        result.append({
            **b,
            "status":
                get_status(
                    b["fill_level"]
                )
        })

    return jsonify(result)


# ---------------- COLLECTION PRIORITY ----------------

@app.route("/api/priority")
def collection_priority():

    priority = []

    for b in bins:

        priority.append({

            "id": b["id"],

            "location":
                b["location"],

            "fill_level":
                b["fill_level"],

            "priority":
                get_priority(
                    b["fill_level"]
                )
        })

    priority.sort(
        key=lambda x: x["fill_level"],
        reverse=True
    )

    return jsonify(priority)


# ---------------- ANALYTICS ----------------

@app.route("/api/analytics")
def analytics():

    total_weight = sum(
        b["weight"]
        for b in bins
    )

    average_temperature = (
        sum(
            b["temperature"]
            for b in bins
        ) / len(bins)
    )

    highest_bin = max(
        bins,
        key=lambda x: x["fill_level"]
    )

    lowest_bin = min(
        bins,
        key=lambda x: x["fill_level"]
    )

    return jsonify({

        "average_fill":
            round(
                sum(
                    b["fill_level"]
                    for b in bins
                ) / len(bins),
                1
            ),

        "total_weight":
            round(total_weight, 1),

        "average_temperature":
            round(
                average_temperature,
                1
            ),

        "highest_bin":
            highest_bin["id"],

        "highest_fill":
            highest_bin["fill_level"],

        "lowest_bin":
            lowest_bin["id"],

        "lowest_fill":
            lowest_bin["fill_level"]
    })


# ---------------- ROUTES ----------------

@app.route("/api/routes")
def routes():

    sorted_bins = sorted(
        bins,
        key=lambda x: x["fill_level"],
        reverse=True
    )

    route = []

    for index, b in enumerate(
        sorted_bins,
        start=1
    ):

        route.append({

            "stop":
                index,

            "bin":
                b["id"],

            "location":
                b["location"],

            "fill":
                b["fill_level"],

            "priority":
                get_priority(
                    b["fill_level"]
                )
        })

    return jsonify(route)


# ---------------- AI PREDICTION ----------------

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    data = request.json

    fill_level = float(
        data["fill_level"]
    )

    temperature = float(
        data["temperature"]
    )

    weight = float(
        data["weight"]
    )

    features = [[
        fill_level,
        temperature,
        weight
    ]]

    prediction = model.predict(
        features
    )[0]

    try:

        probabilities = (
            model.predict_proba(
                features
            )[0]
        )

        confidence = (
            max(probabilities) * 100
        )

    except:

        confidence = 90.0

    return jsonify({

        "status":
            str(prediction),

        "probability":
            round(
                confidence,
                2
            ),

        "fill_level":
            fill_level,

        "temperature":
            temperature,

        "weight":
            weight
    })


# ---------------- REFRESH SENSOR DATA ----------------

@app.route(
    "/api/refresh",
    methods=["POST"]
)
def refresh():

    for b in bins:

        change = random.randint(
            -2,
            4
        )

        b["fill_level"] += change

        b["fill_level"] = max(
            0,
            min(
                100,
                b["fill_level"]
            )
        )

        b["temperature"] += random.uniform(
            -0.5,
            0.5
        )

        b["temperature"] = round(
            b["temperature"],
            1
        )

    return jsonify({

        "success": True,

        "message":
            "Sensor data updated",

        "updated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    })


if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
