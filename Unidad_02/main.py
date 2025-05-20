
import numpy as np
from config import SENSORS, WEIGHTS, ALPHA, BETA
from sensor_data import generate_sensor_values, get_median_values, get_test_scenarios
from satisfaction import calculate_overall_satisfaction, calculate_overall_energy_cost
from smoothing import apply_both_methods
from visualization import display_sensor_comparison, plot_satisfaction_levels

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
