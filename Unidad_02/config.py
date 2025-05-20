
# Sensor configuration (min, max values)
SENSORS = {
    "temperature": {"min": 20, "max": 28, "type": "minimization"},
    "humidity": {"min": 40, "max": 80, "type": "minimization"},
    "noise": {"min": 60, "max": 120, "type": "minimization"},
    "illumination": {"min": 400, "max": 900, "type": "maximization"}
}

# Cost per unit change for each sensor
COSTS = {
    "temperature": 40,
    "humidity": 25,
    "noise": 12,
    "illumination": 3
}

# Weights for each sensor in satisfaction calculation
WEIGHTS = {
    "temperature": 0.4,
    "humidity": 0.2,
    "noise": 0.1,
    "illumination": 0.3
}

# Smoothing parameters
ALPHA = 0.3  # Satisfaction weight
BETA = 0.7   # Energy weight
CORRECTION_COEFFICIENT = 0.2  # "x" in the algorithm
