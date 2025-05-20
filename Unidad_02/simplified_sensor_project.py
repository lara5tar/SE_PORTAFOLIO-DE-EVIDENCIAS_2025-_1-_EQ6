import random
import numpy as np
import matplotlib.pyplot as plt

# Basic sensor configuration 
SENSORS = {
    "temperature": {"min": 20, "max": 28},
    "humidity": {"min": 40, "max": 80},
    "noise": {"min": 60, "max": 120},
    "illumination": {"min": 400, "max": 900}
}

# Single weight for each sensor
IMPORTANCE = {
    "temperature": 0.4,
    "humidity": 0.2,
    "noise": 0.1,
    "illumination": 0.3
}

# Simple smoothing parameter
SMOOTHING_FACTOR = 0.3

def generate_sensor_data(num_readings=20):
    """Generate random sensor readings"""
    data = {}
    for sensor, config in SENSORS.items():
        min_val = config["min"]
        max_val = config["max"]
        # Generate random values with some going outside normal ranges
        data[sensor] = [random.uniform(min_val * 0.8, max_val * 1.2) for _ in range(num_readings)]
    return data

def simple_smoothing(data):
    """Apply simple exponential smoothing to data"""
    smoothed = []
    if not data:
        return []
    
    # Start with the first value
    smoothed.append(data[0])
    
    # Apply smoothing formula: smoothed_t = α * actual + (1-α) * smoothed_(t-1)
    for i in range(1, len(data)):
        smoothed_value = SMOOTHING_FACTOR * data[i] + (1 - SMOOTHING_FACTOR) * smoothed[i-1]
        smoothed.append(smoothed_value)
        
    return smoothed

def calculate_satisfaction(value, min_val, max_val):
    """Calculate satisfaction level on a scale of 0-1"""
    # Simple linear satisfaction model
    if value < min_val:
        return 0.0
    elif value > max_val:
        return 0.0
    else:
        # Value is within ideal range
        position = (value - min_val) / (max_val - min_val)
        # Highest satisfaction (1.0) is in the middle of the range
        return 1.0 - abs(position - 0.5) * 2

def show_comparison_chart(original, smoothed, title):
    """Display simple chart comparing original vs smoothed data"""
    plt.figure(figsize=(10, 5))
    plt.plot(original, 'b-o', alpha=0.7, label='Original Data')
    plt.plot(smoothed, 'r-', linewidth=2, label='Smoothed Data')
    plt.title(title)
    plt.xlabel('Reading Number')
    plt.ylabel('Sensor Value')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Save and show the plot
    plt.savefig(f"/home/lara5tar/Escritorio/SE_PORTAFOLIO-DE-EVIDENCIAS_2025-_1-_EQ6/Unidad_02/{title.replace(' ', '_')}.png")
    plt.show()

def evaluate_sensor_quality(sensor_data):
    """Evaluate how good the sensor readings are"""
    results = {}
    
    for sensor, readings in sensor_data.items():
        min_val = SENSORS[sensor]["min"]
        max_val = SENSORS[sensor]["max"]
        
        # Calculate average satisfaction
        satisfaction_scores = [calculate_satisfaction(value, min_val, max_val) for value in readings]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
        
        results[sensor] = avg_satisfaction
    
    return results

def main():
    print("==== SIMPLIFIED SENSOR PROJECT ====")
    
    # 1. Generate sensor data
    print("\nGenerating sensor data...")
    sensor_data = generate_sensor_data()
    
    # 2. Process and smooth each sensor's data
    print("\nProcessing sensor data...\n")
    for sensor, readings in sensor_data.items():
        print(f"\n--- {sensor.capitalize()} Sensor ---")
        
        # Get raw statistics
        min_reading = min(readings)
        max_reading = max(readings)
        avg_reading = sum(readings) / len(readings)
        
        print(f"Raw readings - Min: {min_reading:.1f}, Max: {max_reading:.1f}, Avg: {avg_reading:.1f}")
        
        # Apply smoothing
        smoothed_readings = simple_smoothing(readings)
        
        # Show smoothed statistics
        min_smoothed = min(smoothed_readings)
        max_smoothed = max(smoothed_readings)
        avg_smoothed = sum(smoothed_readings) / len(smoothed_readings)
        
        print(f"Smoothed readings - Min: {min_smoothed:.1f}, Max: {max_smoothed:.1f}, Avg: {avg_smoothed:.1f}")
        
        # Visualize the comparison
        show_comparison_chart(readings, smoothed_readings, f"{sensor.capitalize()} Data Smoothing")
    
    # 3. Evaluate sensor quality
    print("\nEvaluating sensor quality...")
    quality_scores = evaluate_sensor_quality(sensor_data)
    
    # Show quality bar chart
    plt.figure(figsize=(10, 6))
    sensors = list(quality_scores.keys())
    scores = [quality_scores[s] for s in sensors]
    
    plt.bar(sensors, scores, color='skyblue')
    plt.ylim(0, 1.0)
    plt.title('Sensor Quality Scores')
    plt.ylabel('Quality Score (0-1)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save and show the plot
    plt.savefig("/home/lara5tar/Escritorio/SE_PORTAFOLIO-DE-EVIDENCIAS_2025-_1-_EQ6/Unidad_02/Sensor_Quality_Scores.png")
    plt.show()
    
    print("\nProject execution completed!")

if __name__ == "__main__":
    main()
