#!/usr/bin/env python3
"""
ESP32 Simulator - Proyecto Integrador
Simula el comportamiento del ESP32 para envío de datos de sensores LDR a Firebase
"""

import time
import requests
import json
import random
import numpy as np
from datetime import datetime

# Configuración de Firebase (igual que en el código Arduino)
FIREBASE_URL = "https://embebidos-pi-default-rtdb.firebaseio.com/"

# Definición de constantes
LDR_UPDATE_INTERVAL = 5  # Segundos entre actualizaciones de sensores
CONTROL_CHECK_INTERVAL = 3  # Segundos entre verificaciones de control

# Variables para simulación
light_values = [0, 0, 0, 0]  # Valores de control de intensidad para los 4 focos
last_update_time = 0  # Timestamp de la última actualización

class ESP32Simulator:
    def __init__(self):
        self.running = False
        self.ldr_values = [512, 512, 512, 512]  # Valores iniciales de los LDRs
        self.ambient_light = 0.5  # Luz ambiental (0.0 - 1.0)
        self.light_pattern = "static"  # Patrón de variación de luz: static, random, sine
        
        print("ESP32 Simulator iniciado")
        print("Simulando 4 sensores LDR y enviando datos a Firebase")
        
    def start(self):
        """Inicia la simulación del ESP32"""
        self.running = True
        print("Simulación iniciada")
        
        last_ldr_update = 0
        last_control_check = 0
        
        try:
            while self.running:
                current_time = time.time()
                
                # Enviar datos de sensores a Firebase periódicamente
                if current_time - last_ldr_update >= LDR_UPDATE_INTERVAL:
                    self.update_ldrs_to_firebase()
                    last_ldr_update = current_time
                
                # Verificar señales de control desde Firebase periódicamente
                if current_time - last_control_check >= CONTROL_CHECK_INTERVAL:
                    self.check_control_from_firebase()
                    last_control_check = current_time
                
                # Simular cambios en los valores de los sensores
                self.simulate_sensor_changes()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nSimulación detenida por el usuario")
        except Exception as e:
            print(f"Error en la simulación: {e}")
    
    def update_ldrs_to_firebase(self):
        """Simula la lectura de sensores LDR y envía los datos a Firebase"""
        timestamp = int(time.time())
        
        # Crear JSON con datos
        data = {
            "ldr_value1": self.ldr_values[0],
            "ldr_value2": self.ldr_values[1],
            "ldr_value3": self.ldr_values[2],
            "ldr_value4": self.ldr_values[3],
            "timestamp": timestamp
        }
        
        try:
            # Enviar datos a Firebase
            response = requests.put(
                f"{FIREBASE_URL}/sensores/datos_{timestamp}.json",
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] LDRs enviados a Firebase:")
                print(f"  LDR1: {self.ldr_values[0]} | LDR2: {self.ldr_values[1]} | LDR3: {self.ldr_values[2]} | LDR4: {self.ldr_values[3]}")
            else:
                print(f"Error al enviar LDRs a Firebase: {response.status_code}")
                
        except Exception as e:
            print(f"Error en update_ldrs_to_firebase: {e}")
    
    def check_control_from_firebase(self):
        """Verifica comandos de control en Firebase y actualiza las variables de simulación"""
        try:
            global last_update_time, light_values
            
            # Obtener el último control desde Firebase
            response = requests.get(f"{FIREBASE_URL}/control.json?orderBy=\"timestamp\"&limitToLast=1")
            
            if response.status_code == 200 and response.json():
                control_data = next(iter(response.json().values()))
                timestamp = control_data.get('timestamp', 0)
                
                # Si encontramos una entrada y es más reciente que nuestra última actualización
                if timestamp > last_update_time:
                    values_changed = False
                    
                    # Obtener los valores pwm para los 4 focos
                    for i in range(4):
                        if f"pwm_value{i+1}" in control_data:
                            new_value = int(control_data[f"pwm_value{i+1}"])
                            if new_value != light_values[i]:
                                light_values[i] = new_value
                                values_changed = True
                    
                    # Si algún valor cambió, simulamos un cambio en los focos
                    if values_changed:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Nuevos valores de control desde Firebase (timestamp: {timestamp}):")
                        print(f"  Foco 1: {light_values[0]} | Foco 2: {light_values[1]} | Foco 3: {light_values[2]} | Foco 4: {light_values[3]}")
                        
                        # Ajustar la simulación para reflejar el cambio en los focos
                        self.simulate_light_effect()
                        
                        last_update_time = timestamp
            
        except Exception as e:
            print(f"Error en check_control_from_firebase: {e}")
    
    def simulate_sensor_changes(self):
        """Simula cambios en los valores de los sensores"""
        if self.light_pattern == "static":
            # Mantener valores con pequeñas fluctuaciones
            for i in range(4):
                noise = random.randint(-10, 10)
                base_light = self.ambient_light * 1023
                influence = light_values[i] / 255 * 0.5 * 1023  # La influencia del foco
                self.ldr_values[i] = int(max(0, min(1023, base_light - influence + noise)))
                
        elif self.light_pattern == "random":
            # Cambios aleatorios más pronunciados
            for i in range(4):
                change = random.randint(-50, 50)
                self.ldr_values[i] = max(0, min(1023, self.ldr_values[i] + change))
                
        elif self.light_pattern == "sine":
            # Patrón sinusoidal para simular cambios de luz natural
            t = time.time()
            for i in range(4):
                phase = i * np.pi / 2  # Desplazamiento de fase para cada sensor
                sine_component = np.sin(t/10 + phase) * 200
                base_light = self.ambient_light * 1023
                influence = light_values[i] / 255 * 0.5 * 1023
                self.ldr_values[i] = int(max(0, min(1023, base_light - influence + sine_component)))
    
    def simulate_light_effect(self):
        """Simula el efecto de los cambios en la iluminación (focos) sobre los sensores"""
        # Suponemos que el cambio en el valor de los focos afecta a los sensores
        for i in range(4):
            # La intensidad del foco es inversamente proporcional al valor del sensor LDR
            # (mayor intensidad de luz -> menor valor de LDR)
            light_effect = light_values[i] / 255 * 0.5 * 1023
            self.ldr_values[i] = int(max(0, min(1023, self.ldr_values[i] - light_effect)))
    
    def set_ambient_light(self, value):
        """Establece el nivel de luz ambiental (0.0 - 1.0)"""
        self.ambient_light = max(0.0, min(1.0, value))
        print(f"Luz ambiental establecida a {self.ambient_light:.1f} (0.0-1.0)")
    
    def set_light_pattern(self, pattern):
        """Establece el patrón de variación de luz"""
        valid_patterns = ["static", "random", "sine"]
        if pattern in valid_patterns:
            self.light_pattern = pattern
            print(f"Patrón de luz establecido a '{pattern}'")
        else:
            print(f"Patrón no válido. Opciones: {', '.join(valid_patterns)}")
    
    def stop(self):
        """Detiene la simulación"""
        self.running = False
        print("Simulación detenida")

def main():
    """Función principal"""
    print("=" * 60)
    print("ESP32 SIMULATOR - PROYECTO INTEGRADOR")
    print("Simulador de ESP32 para envío de datos de sensores LDR a Firebase")
    print("=" * 60)
    print("Opciones disponibles:")
    print("1. Iniciar simulación con patrón estático")
    print("2. Iniciar simulación con patrón aleatorio")
    print("3. Iniciar simulación con patrón sinusoidal")
    print("4. Configurar luz ambiental")
    
    option = input("Seleccione una opción (1-4): ")
    
    simulator = ESP32Simulator()
    
    if option == '1':
        simulator.set_light_pattern("static")
        simulator.start()
    elif option == '2':
        simulator.set_light_pattern("random")
        simulator.start()
    elif option == '3':
        simulator.set_light_pattern("sine")
        simulator.start()
    elif option == '4':
        try:
            light_level = float(input("Nivel de luz ambiental (0.0 - 1.0): "))
            simulator.set_ambient_light(light_level)
            pattern = input("Patrón (static/random/sine): ").lower()
            simulator.set_light_pattern(pattern)
            simulator.start()
        except ValueError:
            print("Valor no válido. Debe ser un número entre 0.0 y 1.0")
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()