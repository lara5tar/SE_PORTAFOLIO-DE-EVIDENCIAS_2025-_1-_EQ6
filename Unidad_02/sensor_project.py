import random
import numpy as np
import matplotlib.pyplot as plt

# =========================================================================
# CONFIGURATION PARAMETERS
# =========================================================================

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

# =========================================================================
# SENSOR DATA PROCESSING FUNCTIONS
# =========================================================================

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

# =========================================================================
# SATISFACTION AND ENERGY COST CALCULATIONS
# =========================================================================

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

# =========================================================================
# SMOOTHING ALGORITHMS
# =========================================================================

class Smoother:
    def __init__(self, initial_value=0):
        self.smoothed_value = initial_value
        self.w = 0  # Weight factor
    
    def method1(self, real_value):
        """
        First smoothing method using the formula:
        w = (vReal - vSuavizado) / (vReal + vSuavizado)
        """
        if self.smoothed_value != 0:  # Avoid division by zero
            # Calculate weight based on real and smoothed values
            self.w = (real_value - self.smoothed_value) / (real_value + self.smoothed_value)
            
            # Update smoothed value using weight
            self.smoothed_value = self.smoothed_value + self.w * (real_value - self.smoothed_value)
        else:
            self.smoothed_value = real_value
            
        return self.smoothed_value
    
    def method2(self, real_value):
        """
        Second smoothing method using the formula:
        w = w + x (ValorReal - VaorSuavizado)
        where x is the correction coefficient
        """
        # Update weight using correction coefficient
        self.w = self.w + CORRECTION_COEFFICIENT * (real_value - self.smoothed_value)
        
        # Update smoothed value using weight
        self.smoothed_value = self.smoothed_value + self.w * (real_value - self.smoothed_value)
        
        return self.smoothed_value

def apply_both_methods(data_series):
    """
    Apply both smoothing methods to a series of data and return results for comparison
    """
    smoother1 = Smoother(data_series[0] if data_series else 0)
    smoother2 = Smoother(data_series[0] if data_series else 0)
    
    results_method1 = []
    results_method2 = []
    
    for value in data_series:
        smooth_val1 = smoother1.method1(value)
        smooth_val2 = smoother2.method2(value)
        
        results_method1.append(smooth_val1)
        results_method2.append(smooth_val2)
    
    return results_method1, results_method2

# =========================================================================
# VISUALIZATION FUNCTIONS
# =========================================================================

def plot_smoothing_comparison(original_data, method1_data, method2_data, title="Smoothing Methods Comparison"):
    """Plot comparison between original data and two smoothing methods."""
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(original_data))
    plt.plot(x, original_data, 'o-', label='Original Data', alpha=0.7)
    plt.plot(x, method1_data, 's-', label='Method 1 (w formula)', linewidth=2)
    plt.plot(x, method2_data, '^-', label='Method 2 (correction coeff)', linewidth=2)
    
    plt.xlabel('Sample Index')
    plt.ylabel('Value')
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f"/home/lara5tar/Escritorio/SE_PORTAFOLIO-DE-EVIDENCIAS_2025-_1-_EQ6/Unidad_02/{title.replace(' ', '_')}.png")
    plt.show()

def display_sensor_comparison(sensor_data, smoothed_data_method1, smoothed_data_method2):
    """Display comparison of original and smoothed data for each sensor."""
    for sensor in sensor_data:
        original = sensor_data[sensor]
        method1 = smoothed_data_method1[sensor]
        method2 = smoothed_data_method2[sensor]
        
        plot_smoothing_comparison(
            original, method1, method2, 
            f"Smoothing Comparison for {sensor.capitalize()}"
        )

def plot_satisfaction_levels(satisfaction_data, title="Satisfaction Levels"):
    """Plot satisfaction levels across scenarios."""
    scenarios = list(satisfaction_data.keys())
    satisfaction = [satisfaction_data[s] for s in scenarios]
    
    plt.figure(figsize=(10, 6))
    plt.bar(scenarios, satisfaction, color='skyblue', edgecolor='navy')
    plt.ylim(0, 1.0)
    plt.xlabel('Scenario')
    plt.ylabel('Satisfaction Level')
    plt.title(title)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f"/home/lara5tar/Escritorio/SE_PORTAFOLIO-DE-EVIDENCIAS_2025-_1-_EQ6/Unidad_02/{title.replace(' ', '_')}.png")
    plt.show()

# =========================================================================
# MAIN EXECUTION FUNCTIONS
# =========================================================================

def process_sensor_data_with_smoothing():
    """Process sensor data using both smoothing methods and compare."""
    print("Generating sensor data...")
    raw_sensor_data = generate_sensor_values(num_readings=30)
    
    # Apply both smoothing methods to each sensor's data
    smoothed_data_method1 = {}
    smoothed_data_method2 = {}
    
    for sensor, data in raw_sensor_data.items():
        method1_results, method2_results = apply_both_methods(data)
        smoothed_data_method1[sensor] = method1_results
        smoothed_data_method2[sensor] = method2_results
    
    # Visualize results
    display_sensor_comparison(raw_sensor_data, smoothed_data_method1, smoothed_data_method2)
    
    # Get median values from original and smoothed data
    original_medians = get_median_values(raw_sensor_data)
    smoothed_medians1 = get_median_values(smoothed_data_method1)
    smoothed_medians2 = get_median_values(smoothed_data_method2)
    
    print("\nOriginal Median Values:")
    for sensor, value in original_medians.items():
        print(f"{sensor.capitalize()}: {value:.2f}")
    
    print("\nSmoothed Median Values (Method 1):")
    for sensor, value in smoothed_medians1.items():
        print(f"{sensor.capitalize()}: {value:.2f}")
    
    print("\nSmoothed Median Values (Method 2):")
    for sensor, value in smoothed_medians2.items():
        print(f"{sensor.capitalize()}: {value:.2f}")
    
    return raw_sensor_data, smoothed_data_method1, smoothed_data_method2

def evaluate_scenarios():
    """Evaluate satisfaction and energy costs for different scenarios."""
    scenarios = get_test_scenarios()
    
    # Define a set of recommended values (Vo) for each scenario
    recommended_values = []
    for scenario in scenarios:
        rec_values = {}
        for sensor, value in scenario.items():
            config = SENSORS[sensor]
            # Generate a recommended value within sensor's min-max range
            rec_values[sensor] = np.clip(
                value * np.random.uniform(0.85, 1.15),  # Vary by +/- 15%
                config["min"],
                config["max"]
            )
        recommended_values.append(rec_values)
    
    # Calculate satisfaction and energy costs
    results = {}
    for i, (current, recommended) in enumerate(zip(scenarios, recommended_values)):
        satisfaction = calculate_overall_satisfaction(current, recommended, WEIGHTS)
        energy_cost = calculate_overall_energy_cost(current, recommended, WEIGHTS)
        
        # Combined objective function
        objective = ALPHA * satisfaction + BETA * energy_cost
        
        results[f"Scenario {i+1}"] = objective
        
        print(f"\nScenario {i+1}:")
        print(f"Current values: {current}")
        print(f"Recommended values: {recommended}")
        print(f"Satisfaction: {satisfaction:.4f}")
        print(f"Energy cost satisfaction: {energy_cost:.4f}")
        print(f"Objective function (α={ALPHA}, β={BETA}): {objective:.4f}")
    
    # Visualize results
    plot_satisfaction_levels(results, "Objective Function by Scenario")
    
    return scenarios, recommended_values, results

def main():
    print("=" * 80)
    print("UNIDAD 02 PROJECT: SENSOR DATA PROCESSING AND SMOOTHING")
    print("=" * 80)
    
    # Process sensor data with smoothing
    print("\n--- Part 1: Smoothing Sensor Data ---")
    raw_data, smoothed1, smoothed2 = process_sensor_data_with_smoothing()
    
    # Evaluate scenarios
    print("\n--- Part 2: Evaluating Satisfaction and Energy Costs ---")
    scenarios, recommendations, results = evaluate_scenarios()
    
    print("\nProject execution completed successfully!")

if __name__ == "__main__":
    main()
