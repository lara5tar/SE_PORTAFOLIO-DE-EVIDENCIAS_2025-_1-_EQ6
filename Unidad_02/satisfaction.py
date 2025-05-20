
from config import SENSORS, COSTS

def calculate_satisfaction(sensor, current_value, recommended_value):
    """Calculate satisfaction level for a single sensor."""
    config = SENSORS[sensor]
    min_val = config["min"]
    max_val = config["max"]
    
    if config["type"] == "minimization":
        if current_value <= min_val:
            return 1.0  # Maximum satisfaction
        elif current_value >= max_val:
            return 0.0  # Minimum satisfaction
        else:
            # Decreases linearly from min to max
            return (max_val - current_value) / (max_val - min_val)
    
    else:  # maximization
        if current_value >= max_val:
            return 1.0  # Maximum satisfaction
        elif current_value <= min_val:
            return 0.0  # Minimum satisfaction
        else:
            # Increases linearly from min to max
            return (current_value - min_val) / (max_val - min_val)

def calculate_energy_cost(sensor, current_value, recommended_value):
    """Calculate energy cost to move from current to recommended value."""
    config = SENSORS[sensor]
    min_val = config["min"]
    max_val = config["max"]
    cost_per_unit = COSTS[sensor]
    
    if config["type"] == "minimization":
        # Energy calculations for minimization type sensors
        if current_value <= recommended_value:
            Eo = 0
        else:
            Eo = cost_per_unit + cost_per_unit * (current_value - recommended_value)
        
        if current_value <= min_val:
            Emin = 0
            Emax = 0
        else:
            Emin = 0
            Emax = cost_per_unit + cost_per_unit * (current_value - min_val)
    
    else:  # maximization
        # Energy calculations for maximization type sensors
        if current_value >= recommended_value:
            Eo = 0
        else:
            Eo = cost_per_unit + cost_per_unit * (recommended_value - current_value)
        
        if current_value >= max_val:
            Emin = 0
            Emax = 0
        else:
            Emax = cost_per_unit + cost_per_unit * (max_val - current_value)
            Emin = 0
    
    # Calculate normalized energy satisfaction
    if Emax == Emin:
        return 1.0  # No energy cost or maximum already achieved
    else:
        return 1.0 - ((Eo - Emin) / (Emax - Emin)) if Emax > Emin else 1.0

def calculate_overall_satisfaction(sensor_values, recommended_values, weights):
    """Calculate overall satisfaction based on all sensors and their weights."""
    total_satisfaction = 0
    
    for sensor, weight in weights.items():
        current = sensor_values[sensor]
        recommended = recommended_values[sensor]
        satisfaction = calculate_satisfaction(sensor, current, recommended)
        total_satisfaction += satisfaction * weight
        
    return total_satisfaction

def calculate_overall_energy_cost(sensor_values, recommended_values, weights):
    """Calculate overall energy cost based on all sensors."""
    total_energy_satisfaction = 0
    
    for sensor, weight in weights.items():
        current = sensor_values[sensor]
        recommended = recommended_values[sensor]
        energy_satisfaction = calculate_energy_cost(sensor, current, recommended)
        total_energy_satisfaction += energy_satisfaction * weight
        
    return total_energy_satisfaction
