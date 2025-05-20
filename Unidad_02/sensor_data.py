
import random
import numpy as np
from config import SENSORS

def generate_sensor_values(num_readings=30):
    """Generate random sensor readings within the configured ranges."""
    data = {}
    for sensor, config in SENSORS.items():
        min_val = config["min"]
        max_val = config["max"]
        # Generate random values within range, possibly exceeding slightly
        extended_min = min_val * 0.7
        extended_max = max_val * 1.3
        data[sensor] = [random.uniform(extended_min, extended_max) for _ in range(num_readings)]
    
    return data

def get_median_values(sensor_data):
    """Calculate the median value for each sensor's readings."""
    medians = {}
    for sensor, readings in sensor_data.items():
        medians[sensor] = np.median(readings)
    
    return medians

def get_test_scenarios():
    """Generate test scenarios for comparison."""
    scenarios = []
    
    # Generate test scenarios with values inside and outside ranges
    for _ in range(5):
        scenario = {}
        for sensor, config in SENSORS.items():
            min_val = config["min"]
            max_val = config["max"]
            range_width = max_val - min_val
            
            # 50% chance to be inside range, 50% outside
            if random.random() > 0.5:
                scenario[sensor] = random.uniform(min_val, max_val)
            else:
                # Outside range (either below min or above max)
                if random.random() > 0.5:
                    scenario[sensor] = random.uniform(min_val - range_width * 0.5, min_val)
                else:
                    scenario[sensor] = random.uniform(max_val, max_val + range_width * 0.5)
        
        scenarios.append(scenario)
    
    return scenarios
