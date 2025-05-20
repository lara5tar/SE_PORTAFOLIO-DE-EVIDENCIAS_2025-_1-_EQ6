#!/usr/bin/env python3
"""
Versión simplificada del algoritmo de Recocido Simulado
para el Proyecto Integrador. Usa solo bibliotecas estándar de Python.
"""

import time
import json
import random
import math
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# Configuración de Firebase
FIREBASE_URL = "https://embebidos-pi-default-rtdb.firebaseio.com/"

# Objetivo de intensidad lumínica para cada zona (normalizado entre 0-1)
TARGET_INTENSITIES = [0.65, 0.55, 0.70, 0.60]  # Valores objetivo para los 4 sensores

# Parámetros del recocido simulado
INITIAL_TEMP = 100.0
COOLING_RATE = 0.95
MIN_TEMP = 0.1

class SimplifiedAnnealingController:
    def __init__(self):
        self.zones = 4
        self.temperature = INITIAL_TEMP
        self.current_outputs = [0.5] * self.zones  # Comenzamos con salidas medias
        self.best_outputs = [0.5] * self.zones
        self.best_errors = [float('inf')] * self.zones
        self.iteration = 0
        self.last_firebase_data = None
        
        print("Controlador de Recocido Simulado Simplificado iniciado")
        print(f"Temperatura inicial: {self.temperature}")
        print(f"Tasa de enfriamiento: {COOLING_RATE}")
        print(f"Temperatura mínima: {MIN_TEMP}")
        print(f"Valores objetivo: {[t*100 for t in TARGET_INTENSITIES]}%")
    
    def firebase_get(self, path, query=""):
        """Lee datos de Firebase usando urllib"""
        try:
            # Quitar la primera / si existe para evitar doble barra
            if path.startswith("/"):
                path = path[1:]
                
            url = f"{FIREBASE_URL}{path}.json{query}"
            print(f"GET URL: {url}")
            with urllib.request.urlopen(url) as response:
                if response.code == 200:
                    return json.loads(response.read().decode('utf-8'))
            return None
        except Exception as e:
            print(f"Error en firebase_get: {e}")
            return None
    
    def firebase_put(self, path, data):
        """Envía datos a Firebase usando urllib"""
        try:
            # Quitar la primera / si existe para evitar doble barra
            if path.startswith("/"):
                path = path[1:]
                
            url = f"{FIREBASE_URL}{path}.json"
            print(f"PUT URL: {url}")
            data_json = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_json, method='PUT')
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req) as response:
                return response.code == 200
        except Exception as e:
            print(f"Error en firebase_put: {e}")
            return False
    
    def read_sensors(self):
        """Lee los valores de los sensores desde Firebase"""
        try:
            # Obtener los últimos datos de los sensores en Firebase
            sensor_data = self.firebase_get("sensores")
            
            if sensor_data and isinstance(sensor_data, dict):
                # Buscar el sensor con el timestamp más alto
                highest_timestamp = 0
                latest_sensor = None
                
                for key, values in sensor_data.items():
                    if isinstance(values, dict) and 'timestamp' in values:
                        timestamp = int(values['timestamp'])
                        if timestamp > highest_timestamp:
                            highest_timestamp = timestamp
                            latest_sensor = values
                
                if latest_sensor:
                    self.last_firebase_data = latest_sensor
                    return [
                        latest_sensor.get('ldr_value1', 512),
                        latest_sensor.get('ldr_value2', 512),
                        latest_sensor.get('ldr_value3', 512),
                        latest_sensor.get('ldr_value4', 512)
                    ]
            
            # Si no hay nuevos datos, usar los últimos que teníamos
            if self.last_firebase_data:
                return [
                    self.last_firebase_data.get('ldr_value1', 512),
                    self.last_firebase_data.get('ldr_value2', 512),
                    self.last_firebase_data.get('ldr_value3', 512),
                    self.last_firebase_data.get('ldr_value4', 512)
                ]
        except Exception as e:
            print(f"Error leyendo sensores: {e}")
        
        # Si todo falla, retornar valores por defecto
        return [512, 512, 512, 512]
    
    def send_control_signals(self, outputs):
        """Envía las señales de control para los focos a Firebase"""
        timestamp = int(time.time())
        
        # Convertir valores normalizados (0-1) a PWM (0-255)
        pwm_values = [int(output * 255) for output in outputs]
        
        # Crear payload
        data = {
            "timestamp": timestamp,
            "heuristic": "Recocido Simulado Simplificado",
            "temperature": self.temperature
        }
        
        # Añadir valores de salida para cada zona
        for i, (output, pwm) in enumerate(zip(outputs, pwm_values)):
            data[f"output_value{i+1}"] = output
            data[f"pwm_value{i+1}"] = pwm
        
        # Enviar a Firebase
        path = f"control/{timestamp}"
        if self.firebase_put(path, data):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Señales de control enviadas:")
            for i in range(self.zones):
                print(f"  Foco {i+1}: {outputs[i]:.2f} ({pwm_values[i]})")
            return True
        else:
            print("Error al enviar señales de control")
            return False
    
    def create_neighbor_solutions(self):
        """Genera soluciones vecinas proporcionales a la temperatura actual"""
        new_outputs = []
        # La amplitud de la perturbación es proporcional a la temperatura
        max_change = 0.3 * (self.temperature / INITIAL_TEMP)
        
        for current in self.current_outputs:
            # Generar un valor vecino con perturbación aleatoria
            change = random.uniform(-max_change, max_change)
            new_output = current + change
            # Limitar salida entre 0 y 1
            new_output = max(0, min(1, new_output))
            new_outputs.append(new_output)
        
        return new_outputs
    
    def calculate_next_outputs(self, sensor_values):
        """Implementa el algoritmo de Recocido Simulado para determinar las próximas señales"""
        # Normalizar valores de los sensores (0-1)
        normalized_sensors = [value / 1023.0 for value in sensor_values]
        
        # Calcular errores actuales respecto a los objetivos
        current_errors = [abs(target - normalized) for target, normalized in zip(TARGET_INTENSITIES, normalized_sensors)]
        
        # Si la temperatura ya es muy baja, usar las mejores soluciones encontradas
        if self.temperature <= MIN_TEMP:
            outputs = self.best_outputs.copy()
            print(f"Temperatura mínima alcanzada ({self.temperature:.4f}). Usando mejores soluciones encontradas.")
        else:
            # Generar soluciones vecinas
            new_outputs = self.create_neighbor_solutions()
            
            # Evaluar si aceptamos los nuevos valores para cada zona
            for i in range(self.zones):
                # Predecir si el cambio nos acerca o aleja del objetivo
                light_too_low = normalized_sensors[i] < TARGET_INTENSITIES[i]
                
                # Estimar si el cambio es favorable
                # Si la luz es baja y aumentamos la salida, o si la luz es alta y disminuimos la salida
                change_is_favorable = (light_too_low and new_outputs[i] > self.current_outputs[i]) or \
                                    (not light_too_low and new_outputs[i] < self.current_outputs[i])
                
                # Aplica el criterio de aceptación del recocido simulado
                if change_is_favorable:
                    # Si el cambio parece favorable, aceptarlo
                    self.current_outputs[i] = new_outputs[i]
                else:
                    # Si no es favorable, aceptarlo con probabilidad que depende de la temperatura
                    acceptance_probability = math.exp(-current_errors[i] / self.temperature)
                    if random.random() < acceptance_probability:
                        self.current_outputs[i] = new_outputs[i]
            
            # Enfriar la temperatura
            self.temperature *= COOLING_RATE
            
            outputs = self.current_outputs.copy()
        
        # Actualizar mejores soluciones si corresponde
        for i in range(self.zones):
            if current_errors[i] < self.best_errors[i]:
                self.best_errors[i] = current_errors[i]
                self.best_outputs[i] = self.current_outputs[i]
                print(f"Nueva mejor solución para zona {i+1}: {self.best_outputs[i]:.4f} (error: {self.best_errors[i]:.4f})")
        
        self.iteration += 1
        return outputs
    
    def run(self, duration_seconds=600, sample_interval=5):
        """Ejecuta el controlador durante un periodo de tiempo"""
        print(f"Iniciando controlador de luz con Recocido Simulado para {self.zones} zonas")
        print(f"Duración: {duration_seconds} segundos, intervalo: {sample_interval} segundos")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration_seconds:
                # Leer sensores desde Firebase
                sensor_values = self.read_sensors()
                normalized_sensors = [v / 1023.0 for v in sensor_values]
                
                # Calcular errores respecto a los objetivos
                errors = [abs(target - normalized) for target, normalized in zip(TARGET_INTENSITIES, normalized_sensors)]
                
                # Calcular salidas según el recocido simulado
                outputs = self.calculate_next_outputs(sensor_values)
                
                # Enviar señales de control a Firebase
                self.send_control_signals(outputs)
                
                # Mostrar información
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iteración {self.iteration}, Temperatura: {self.temperature:.2f}")
                print("Valores de sensores:")
                for i in range(self.zones):
                    print(f"  Zona {i+1}: Sensor={sensor_values[i]} ({normalized_sensors[i]:.2f}) | "
                          f"Objetivo={TARGET_INTENSITIES[i]:.2f} | Error={errors[i]:.2f}")
                
                # Esperar antes de la siguiente iteración
                time.sleep(sample_interval)
        
        except KeyboardInterrupt:
            print("\nControlador detenido por el usuario")
        except Exception as e:
            print(f"Error en el controlador: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("RECOCIDO SIMULADO SIMPLIFICADO - PROYECTO INTEGRADOR")
    print("Control de intensidad lumínica con algoritmo de Recocido Simulado")
    print("=" * 60)

    # Crear y ejecutar el controlador
    controller = SimplifiedAnnealingController()
    
    # Solicitar duración e intervalo
    try:
        duration = int(input("Duración del controlador en segundos (predeterminado: 600): ") or "600")
        interval = float(input("Intervalo de muestreo en segundos (predeterminado: 5): ") or "5")
        controller.run(duration, interval)
    except ValueError:
        print("Valor no válido. Usando valores predeterminados.")
        controller.run()