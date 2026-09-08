from flask import Flask, render_template, request, jsonify
import joblib
import random
from datetime import datetime

app = Flask(__name__)


# =========================================================
# LOAD MACHINE LEARNING MODEL
# =========================================================

try:
    model = joblib.load("dustbin_model.pkl")
    print("AI Model loaded successfully.")

except Exception as e:
    model = None
    print("Warning: AI model could not be loaded.")
    print(e)


# =========================================================
# SMART BIN DATA
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


        # -----------------------------------------
        # ML MODEL PREDICTION
        # -----------------------------------------

        if model is not None:

            prediction = model.predict(
                features
            )[0]

            prediction = str(
                prediction
            )

            try:

                probabilities = model.predict_proba(
                    features
                )[0]

                confidence = max(
                    probabilities
                ) * 100

            except Exception:

                confidence = 90.0

        else:

            # Backup rule-based prediction
            # if model is unavailable

            if fill_level >= 85:

                prediction = "FULL"

                confidence = 95.0

            elif fill_level >= 60:

                prediction = "WARNING"

                confidence = 90.0

            else:

                prediction = "NORMAL"

                confidence = 88.0


        # -----------------------------------------
        # RESPONSE
        # -----------------------------------------

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


        if fill >= 85:

            status = "FULL"

        elif fill >= 60:

            status = "WARNING"

        else:

            status = "NORMAL"


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
# DASHBOARD API
# =========================================================

@app.route("/api/dashboard")
def dashboard():

    total_bins = len(bins)


    # Bins which need attention

    action_bins = sum(

        1

        for b in bins

        if b["fill_level"] >= 60

    )


    # Average fill

    average_fill = (

        sum(
            b["fill_level"]
            for b in bins
        )

        / total_bins

    )


    # Highest filled bin

    next_bin = max(

        bins,

        key=lambda x:
        x["fill_level"]

    )


    fill = next_bin[
        "fill_level"
    ]


    # -----------------------------------------
    # OVERFLOW ESTIMATION
    # -----------------------------------------

    if fill >= 90:

        overflow_hours = 2.4

    elif fill >= 75:

        overflow_hours = 5.0

    elif fill >= 60:

        overflow_hours = 8.0

    else:

        overflow_hours = 14.0


    return jsonify({

        "total_bins":
            total_bins,

        "action_bins":
            action_bins,

        "average_fill":
            round(
                average_fill,
                1
            ),

        "next_overflow_bin":
            next_bin["id"],

        "overflow_hours":
            overflow_hours,

        "ai_confidence":
            94.2

    })


# =========================================================
# COLLECTION PRIORITY
# =========================================================

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

            "id":
                b["id"],

            "location":
                b["location"],

            "fill_level":
                fill,

            "priority":
                level

        })


    # Highest fill first

    priority.sort(

        key=lambda x:
        x["fill_level"],

        reverse=True

    )


    return jsonify(priority)


# =========================================================
# REFRESH / SIMULATE SENSOR DATA
# =========================================================

@app.route(
    "/api/refresh",
    methods=["POST"]
)
def refresh():

    for b in bins:


        # Simulate fill level change

        change = random.randint(
            -2,
            4
        )


        b["fill_level"] += change


        # Keep between 0 and 100

        b["fill_level"] = max(

            0,

            min(
                100,
                b["fill_level"]
            )

        )


        # Simulate temperature

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
# AUTOMATIC AI ROUTE
# =========================================================

@app.route("/api/routes/automatic")
def automatic_route():


    # -----------------------------------------
    # Sort bins by fill level
    # Highest priority first
    # -----------------------------------------

    sorted_bins = sorted(

        bins,

        key=lambda x:
        x["fill_level"],

        reverse=True

    )


    route = []


    for b in sorted_bins:

        fill = b["fill_level"]


        # -----------------------------------------
        # Determine priority
        # -----------------------------------------

        if fill >= 85:

            priority = "HIGH"

        elif fill >= 60:

            priority = "MEDIUM"

        else:

            priority = "LOW"


        route.append({

            "id":
                b["id"],

            "location":
                b["location"],

            "fill_level":
                fill,

            "priority":
                priority

        })


    # -----------------------------------------
    # Statistics
    # -----------------------------------------

    total_stops = len(
        route
    )


    high_priority = sum(

        1

        for b in route

        if b["priority"] == "HIGH"

    )


    # -----------------------------------------
    # Estimated distance
    #
    # Demo calculation:
    # Each stop = 2.4 km
    # -----------------------------------------

    distance = round(

        total_stops * 2.4,

        1

    )


    # -----------------------------------------
    # Estimated time
    #
    # Each stop = 8 minutes
    # -----------------------------------------

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
# CREATE MANUAL ROUTE
# =========================================================

@app.route(
    "/api/routes/create",
    methods=["POST"]
)
def create_route():


    try:

        data = request.get_json()


        # -----------------------------------------
        # Vehicle
        # -----------------------------------------

        vehicle = data.get(

            "vehicle",

            "TRUCK-01"

        )


        # -----------------------------------------
        # Selected bin IDs
        # -----------------------------------------

        selected_ids = data.get(

            "bins",

            []

        )


        selected_bins = []


        # -----------------------------------------
        # Find selected bins
        # -----------------------------------------

        for b in bins:

            if b["id"] in selected_ids:


                fill = b[
                    "fill_level"
                ]


                if fill >= 85:

                    priority = "HIGH"

                elif fill >= 60:

                    priority = "MEDIUM"

                else:

                    priority = "LOW"


                selected_bins.append({

                    "id":
                        b["id"],

                    "location":
                        b["location"],

                    "fill_level":
                        fill,

                    "priority":
                        priority

                })


        # -----------------------------------------
        # Sort selected bins
        # -----------------------------------------

        selected_bins.sort(

            key=lambda x:
            x["fill_level"],

            reverse=True

        )


        # -----------------------------------------
        # Route statistics
        # -----------------------------------------

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

            "error":
                str(e)

        }), 400


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
