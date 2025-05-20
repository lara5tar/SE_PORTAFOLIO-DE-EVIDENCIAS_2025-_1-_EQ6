
from config import CORRECTION_COEFFICIENT

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
