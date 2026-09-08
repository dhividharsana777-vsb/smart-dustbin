from flask import Flask, render_template, request, jsonify
import joblib
import random
from datetime import datetime

app = Flask(__name__)

# =========================================================
# AI MODEL LOAD
# =========================================================

try:
    model = joblib.load("dustbin_model.pkl")
    print("AI Model loaded successfully.")
except Exception as e:
    model = None
    print("Warning: AI model could not be loaded.")
    print(e)


# =========================================================
# SMART DUSTBIN SENSOR DATA
# =========================================================

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


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_status(fill):
    """Return bin status based on fill percentage."""

    if fill >= 85:
        return "FULL"

    elif fill >= 60:
        return "WARNING"

    else:
        return "NORMAL"


def get_priority(fill):
    """Return collection priority."""

    if fill >= 85:
        return "HIGH"

    elif fill >= 60:
        return "MEDIUM"

    else:
        return "LOW"


def calculate_route_score(bin_data):
    """
    Calculate AI-inspired collection priority score.

    Higher score = more important to collect first.
    """

    fill = bin_data["fill_level"]
    temperature = bin_data["temperature"]
    weight = bin_data["weight"]

    # Fill level has highest importance
    fill_score = fill * 0.60

    # Heavy bins get higher priority
    weight_score = min(weight, 30) / 30 * 20

    # Higher temperature slightly increases priority
    temperature_score = max(0, temperature - 25) * 2

    total_score = fill_score + weight_score + temperature_score

    return round(total_score, 2)


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# ROUTES PAGE
# =========================================================

@app.route("/routes")
def routes():
    return render_template("routes.html")


# =========================================================
# AI PREDICTION
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        fill_level = float(data["fill_level"])
        temperature = float(data["temperature"])
        weight = float(data["weight"])

        features = [[
            fill_level,
            temperature,
            weight
        ]]

        # -------------------------------------------------
        # USE ML MODEL
        # -------------------------------------------------

        if model is not None:

            prediction = str(
                model.predict(features)[0]
            )

            try:

                probabilities = model.predict_proba(features)[0]

                confidence = max(probabilities) * 100

            except Exception:

                confidence = 90.0

        # -------------------------------------------------
        # FALLBACK AI LOGIC
        # -------------------------------------------------

        else:

            if fill_level >= 85:

                prediction = "FULL"
                confidence = 95.0

            elif fill_level >= 60:

                prediction = "WARNING"
                confidence = 90.0

            else:

                prediction = "NORMAL"
                confidence = 88.0

        return jsonify({

            "status": prediction,

            "probability": round(
                confidence,
                2
            ),

            "fill_level": fill_level,

            "temperature": temperature,

            "weight": weight

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400


# =========================================================
# GET ALL SMART BINS
# =========================================================

@app.route("/api/bins")
def get_bins():

    result = []

    for b in bins:

        fill = b["fill_level"]

        status = get_status(fill)

        result.append({

            "id": b["id"],

            "location": b["location"],

            "fill_level": b["fill_level"],

            "temperature": b["temperature"],

            "weight": b["weight"],

            "status": status

        })

    return jsonify(result)


# =========================================================
# DASHBOARD ANALYTICS
# =========================================================

@app.route("/api/dashboard")
def dashboard():

    total_bins = len(bins)

    action_bins = sum(
        1
        for b in bins
        if b["fill_level"] >= 60
    )

    average_fill = (
        sum(
            b["fill_level"]
            for b in bins
        )
        / total_bins
    )

    next_bin = max(
        bins,
        key=lambda x: x["fill_level"]
    )

    fill = next_bin["fill_level"]

    # Estimated overflow time
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

        "average_fill": round(
            average_fill,
            1
        ),

        "next_overflow_bin": next_bin["id"],

        "overflow_hours": overflow_hours,

        "ai_confidence": 94.2

    })


# =========================================================
# COLLECTION PRIORITY
# =========================================================

@app.route("/api/priority")
def collection_priority():

    priority = []

    for b in bins:

        fill = b["fill_level"]

        level = get_priority(fill)

        score = calculate_route_score(b)

        priority.append({

            "id": b["id"],

            "location": b["location"],

            "fill_level": fill,

            "priority": level,

            "score": score

        })

    # Highest priority first
    priority.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return jsonify(priority)


# =========================================================
# REFRESH SENSOR DATA
# =========================================================

@app.route("/api/refresh", methods=["POST"])
def refresh():

    for b in bins:

        # Simulate IoT sensor update

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

        # Temperature fluctuation

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


# =========================================================
# AI AUTOMATIC COLLECTION ROUTE
# =========================================================

@app.route("/api/routes/automatic")
def automatic_route():

    route = []

    # -----------------------------------------------------
    # Calculate AI score for every bin
    # -----------------------------------------------------

    for b in bins:

        fill = b["fill_level"]

        priority = get_priority(
            fill
        )

        score = calculate_route_score(
            b
        )

        route.append({

            "id": b["id"],

            "location": b["location"],

            "fill_level": fill,

            "priority": priority,

            "score": score

        })

    # -----------------------------------------------------
    # Sort using AI score
    # -----------------------------------------------------

    route.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # -----------------------------------------------------
    # Add collection sequence
    # -----------------------------------------------------

    for index, item in enumerate(
        route,
        start=1
    ):

        item["sequence"] = index

    total_stops = len(route)

    high_priority = sum(

        1
        for b in route
        if b["priority"] == "HIGH"

    )

    # Demo route estimates
    distance = round(
        total_stops * 2.4,
        1
    )

    time = total_stops * 8

    return jsonify({

        "vehicle":
            "AI AUTO ROUTE",

        "total_stops":
            total_stops,

        "high_priority":
            high_priority,

        "distance":
            distance,

        "time":
            time,

        "route":
            route

    })


# =========================================================
# CREATE MANUAL COLLECTION ROUTE
# =========================================================

@app.route(
    "/api/routes/create",
    methods=["POST"]
)
def create_route():

    try:

        data = request.get_json()

        vehicle = data.get(
            "vehicle",
            "TRUCK-01"
        )

        selected_ids = data.get(
            "bins",
            []
        )

        selected_bins = []

        # -------------------------------------------------
        # Find selected bins
        # -------------------------------------------------

        for b in bins:

            if b["id"] in selected_ids:

                fill = b["fill_level"]

                priority = get_priority(
                    fill
                )

                score = calculate_route_score(
                    b
                )

                selected_bins.append({

                    "id":
                        b["id"],

                    "location":
                        b["location"],

                    "fill_level":
                        fill,

                    "priority":
                        priority,

                    "score":
                        score

                })

        # -------------------------------------------------
        # Sort selected bins by AI score
        # -------------------------------------------------

        selected_bins.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # -------------------------------------------------
        # Add route sequence
        # -------------------------------------------------

        for index, item in enumerate(
            selected_bins,
            start=1
        ):

            item["sequence"] = index

        total_stops = len(
            selected_bins
        )

        high_priority = sum(

            1
            for b in selected_bins
            if b["priority"] == "HIGH"

        )

        distance = round(
            total_stops * 2.4,
            1
        )

        time = total_stops * 8

        return jsonify({

            "vehicle":
                vehicle,

            "total_stops":
                total_stops,

            "high_priority":
                high_priority,

            "distance":
                distance,

            "time":
                time,

            "route":
                selected_bins

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400


# =========================================================
# ROUTE OPTIMIZATION DETAILS
# =========================================================

@app.route("/api/routes/optimized")
def optimized_route():

    route = []

    for b in bins:

        score = calculate_route_score(
            b
        )

        priority = get_priority(
            b["fill_level"]
        )

        route.append({

            "id":
                b["id"],

            "location":
                b["location"],

            "fill_level":
                b["fill_level"],

            "temperature":
                b["temperature"],

            "weight":
                b["weight"],

            "priority":
                priority,

            "ai_score":
                score

        })

    # Highest AI score first
    route.sort(
        key=lambda x: x["ai_score"],
        reverse=True
    )

    # Add sequence number
    for index, item in enumerate(
        route,
        start=1
    ):

        item["sequence"] = index

    return jsonify({

        "algorithm":
            "AI Priority Route Optimization",

        "total_bins":
            len(route),

        "route":
            route

    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({

        "status":
            "online",

        "service":
            "SmartWaste AI",

        "time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
