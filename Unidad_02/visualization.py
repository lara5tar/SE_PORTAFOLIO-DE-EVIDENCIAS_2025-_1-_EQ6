
import matplotlib.pyplot as plt
import numpy as np

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
