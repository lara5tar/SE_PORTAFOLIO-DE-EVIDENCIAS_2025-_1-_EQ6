#!/usr/bin/env python3
"""
Proyecto Integrador - Sistema de Control de Intensidad Lumínica
Implementación simplificada del algoritmo de Recocido Simulado para control de iluminación con un solo sensor
Usa solo bibliotecas estándar de Python
"""

import time
import json
import random
import math
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# Configuración de conexión con Firebase
FIREBASE_URL = "https://embebidos-pi-default-rtdb.firebaseio.com/"

# Objetivo de intensidad lumínica (normalizado entre 0-1)
TARGET_INTENSITY = 0.65  # Valor objetivo para el sensor LDR

class SimpleAnnealingController:
    def __init__(self, initial_temp=100, cooling_rate=0.95, min_temp=0.1):
        self.name = "Recocido Simulado"
        self.description = "Control basado en Recocido Simulado para iluminación"
        self.temperature = initial_temp
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        
        # Estado actual y mejor estado
        self.current_output = 0.5  # Comenzamos con salida media
        self.best_output = 0.5
        self.best_error = float('inf')
        
        self.iteration = 0
        self.reset_temp_interval = 50  # Reiniciar temperatura cada 50 iteraciones
        
        # Datos para análisis
        self.sensors_history = []
        self.outputs_history = []
        self.temperature_history = []
        self.error_history = []
        self.timestamp_history = []
        self.last_firebase_data = None
    
    def create_neighbor_solution(self):
        """Genera una solución vecina con perturbación proporcional a la temperatura."""
        max_change = 0.3 * (self.temperature / self.initial_temp)
        
        # Generar un valor vecino con perturbación proporcional a la temperatura
        change = random.uniform(-max_change, max_change)
        new_output = self.current_output + change
        # Limitar salida entre 0 y 1
        new_output = max(0, min(1, new_output))
            
        return new_output
    
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
    
    def read_sensor_from_firebase(self):
        """Lee el valor del sensor desde Firebase"""
        try:
            # Obtener los últimos datos del sensor en Firebase
            sensor_data = self.firebase_get("sensores", "?orderBy=\"timestamp\"&limitToLast=1")
            
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
                
                if latest_sensor and 'ldr_value' in latest_sensor:
                    self.last_firebase_data = latest_sensor
                    return latest_sensor.get('ldr_value', 512)
            
            # Si no se pueden obtener datos o no están disponibles, usar último valor conocido o simulación
            if self.last_firebase_data and 'ldr_value' in self.last_firebase_data:
                return self.last_firebase_data.get('ldr_value', 512)
                
        except Exception as e:
            print(f"Error leyendo datos de Firebase: {e}")
            
        # Si no hay datos, simular valor
        # Valor base + ruido + tendencia según hora del día
        hour = datetime.now().hour
        base = 512  # Valor medio
        day_factor = 1.0 if 8 <= hour <= 18 else 0.3  # Día/noche
        
        trend = base * day_factor
        noise = random.uniform(-50, 50)  # Usando random en lugar de numpy
        return max(0, min(1023, int(trend + noise)))
    
    def send_control_signal_to_firebase(self, output):
        """Envía la señal de control para el foco a Firebase"""
        try:
            # Convertir valor normalizado (0-1) a PWM (0-255)
            pwm_value = int(output * 255)
            
            # Crear payload
            timestamp = int(time.time())
            data = {
                "timestamp": timestamp,
                "heuristic": self.name,
                "temperature": self.temperature,
                "output_value": output,
                "pwm_value": pwm_value
            }
            
            # Enviar a Firebase
            return self.firebase_put(f"control/{timestamp}", data)
                
        except Exception as e:
            print(f"Error en send_control_signal_to_firebase: {e}")
            return False
    
    def log_to_firebase(self, sensor_value, output_value):
        """Registra datos en Firebase para análisis posterior"""
        try:
            # Crear payload
            timestamp = int(time.time())
            
            # Normalizar valor del sensor
            normalized_sensor = sensor_value / 1023.0
            error = abs(TARGET_INTENSITY - normalized_sensor)
            
            # Datos a enviar
            data = {
                "timestamp": timestamp,
                "temperature": self.temperature,
                "heuristic": self.name,
                "sensor_value": sensor_value,
                "normalized_value": normalized_sensor,
                "output_value": output_value,
                "error": error,
                "target": TARGET_INTENSITY
            }
            
            # Enviar a Firebase
            return self.firebase_put(f"recocido_simulado/{timestamp}", data)
                
        except Exception as e:
            print(f"Error en log_to_firebase: {e}")
            return False
    
    def calculate_next_output(self, sensor_value):
        """
        Implementa el algoritmo de Recocido Simulado para determinar
        la próxima señal de control para el foco
        """
        # Normalizar valor del sensor
        normalized_sensor = sensor_value / 1023.0
        
        # Calcular error actual respecto al objetivo
        current_error = abs(TARGET_INTENSITY - normalized_sensor)
        
        # Reiniciar temperatura periódicamente para escapar de óptimos locales
        if self.iteration % self.reset_temp_interval == 0 and self.iteration > 0:
            print(f"Reiniciando temperatura a {self.initial_temp} (iteración {self.iteration})")
            self.temperature = self.initial_temp
            
        # Si la temperatura ya es muy baja, usar la mejor solución encontrada
        if self.temperature <= self.min_temp:
            output = self.best_output
            print(f"Temperatura mínima alcanzada ({self.temperature:.4f}). Usando mejor solución encontrada.")
        else:
            # Generar solución vecina
            new_output = self.create_neighbor_solution()
            
            # Predecir si el cambio nos acerca o aleja del objetivo
            light_too_low = normalized_sensor < TARGET_INTENSITY
            
            # Estimar si el cambio es favorable
            change_is_favorable = (light_too_low and new_output > self.current_output) or \
                                 (not light_too_low and new_output < self.current_output)
            
            # Aplica el criterio de aceptación del recocido simulado
            if change_is_favorable:
                # Si el cambio parece favorable, aceptarlo
                self.current_output = new_output
            else:
                # Si no es favorable, aceptarlo con probabilidad que depende de la temperatura
                acceptance_probability = math.exp(-current_error / self.temperature)
                if random.random() < acceptance_probability:
                    self.current_output = new_output
            
            # Enfriar la temperatura
            self.temperature *= self.cooling_rate
            
            output = self.current_output
            
        # Actualizar mejor solución si corresponde
        if current_error < self.best_error:
            self.best_error = current_error
            self.best_output = self.current_output
            print(f"Nueva mejor solución: {self.best_output:.4f} (error: {self.best_error:.4f})")
            
        # Registrar para análisis
        self.error_history.append(current_error)
        self.temperature_history.append(self.temperature)
        
        self.iteration += 1
        return output
    
    def save_results_to_file(self):
        """Guarda los resultados en un archivo de texto (reemplaza la generación de gráficos)"""
        try:
            with open('resultados_recocido_simulado.txt', 'w') as f:
                f.write("RESULTADOS DE ANÁLISIS CON RECOCIDO SIMULADO\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duración del análisis: {len(self.timestamp_history)} muestras\n")
                f.write(f"Temperatura inicial: {self.initial_temp}\n")
                f.write(f"Factor de enfriamiento: {self.cooling_rate}\n")
                f.write(f"Temperatura final: {self.temperature:.4f}\n\n")
                
                f.write("HISTORIAL DE VALORES\n")
                f.write("Tiempo,Sensor,Salida,Temperatura,Error\n")
                
                for i in range(len(self.timestamp_history)):
                    f.write(f"{self.timestamp_history[i]:.1f},{self.sensors_history[i]},")
                    f.write(f"{self.outputs_history[i]:.4f},{self.temperature_history[i]:.4f},")
                    f.write(f"{self.error_history[i]:.4f}\n")
                
                if len(self.error_history) > 0:
                    # Calcular estadísticas básicas
                    avg_error = sum(self.error_history) / len(self.error_history)
                    
                    f.write(f"\nObjetivo: {TARGET_INTENSITY*100:.1f}%\n")
                    f.write(f"Error promedio: {avg_error:.4f}\n")
                    f.write(f"Mejor salida encontrada: {self.best_output:.4f}\n")
                    f.write(f"Mejor error logrado: {self.best_error:.4f}\n")
            
            print(f"Resultados guardados en 'resultados_recocido_simulado.txt'")
            return True
        except Exception as e:
            print(f"Error guardando resultados: {e}")
            return False
    
    def run(self, duration_seconds=600, sample_interval=1):
        """Ejecuta el controlador durante un periodo de tiempo"""
        print(f"Iniciando controlador de luz con Recocido Simulado")
        print(f"Duración: {duration_seconds} segundos")
        print(f"Objetivo de intensidad: {TARGET_INTENSITY*100}%")
        print(f"Temperatura inicial: {self.temperature}")
        print(f"Factor de enfriamiento: {self.cooling_rate}")
        print(f"Temperatura mínima: {self.min_temp}")
        print(f"Obteniendo datos de Firebase y enviando resultados")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while time.time() - start_time < duration_seconds:
                # Tiempo actual relativo al inicio
                current_time = time.time() - start_time
                
                # Leer sensor desde Firebase
                sensor_value = self.read_sensor_from_firebase()
                normalized_sensor = sensor_value / 1023.0
                
                # Calcular error respecto al objetivo
                error = abs(TARGET_INTENSITY - normalized_sensor)
                
                # Calcular salida según el recocido simulado
                output = self.calculate_next_output(sensor_value)
                
                # Enviar señal de control a Firebase
                self.send_control_signal_to_firebase(output)
                
                # Registrar historial
                self.sensors_history.append(sensor_value)
                self.outputs_history.append(output)
                self.timestamp_history.append(current_time)
                
                # Loggear a Firebase cada 5 iteraciones para no saturar
                if iteration % 5 == 0:
                    self.log_to_firebase(sensor_value, output)
                
                # Mostrar progreso
                if iteration % 10 == 0:
                    print(f"[{current_time:.1f}s] Temperatura: {self.temperature:.2f}")
                    print(f"  Sensor={sensor_value} ({normalized_sensor:.2f}) | "
                          f"Objetivo={TARGET_INTENSITY:.2f} | Output={output:.2f} | Error={error:.2f}")
                    print("-" * 50)
                
                iteration += 1
                time.sleep(sample_interval)
                
        except KeyboardInterrupt:
            print("\nControlador detenido por el usuario")
        except Exception as e:
            print(f"Error en el controlador: {e}")
        finally:
            # Realizar análisis final
            self.final_analysis()
                
    def final_analysis(self):
        """Realiza análisis estadístico final del rendimiento"""
        print("\n--- ANÁLISIS FINAL DEL RECOCIDO SIMULADO ---")
        
        # Calcular métricas
        if len(self.error_history) > 0:
            avg_error = sum(self.error_history) / len(self.error_history)
            
            print(f"Objetivo: {TARGET_INTENSITY*100:.1f}%")
            print(f"Error promedio: {avg_error:.4f}")
            print(f"Mejor salida encontrada: {self.best_output:.4f}")
            print(f"Mejor error logrado: {self.best_error:.4f}")
            
            # Guardar resultados en archivo
            self.save_results_to_file()
            
            # Enviar resultados finales a Firebase
            try:
                final_result = {
                    "timestamp": int(time.time()),
                    "avg_error": avg_error,
                    "initial_temp": self.initial_temp,
                    "cooling_rate": self.cooling_rate,
                    "final_temp": self.temperature,
                    "target": TARGET_INTENSITY,
                    "best_output": self.best_output,
                    "best_error": self.best_error
                }
                
                # Enviar a Firebase
                if self.firebase_put("resultados_finales/" + str(int(time.time())), final_result):
                    print("Resultados finales enviados a Firebase")
                else:
                    print("Error al enviar resultados finales a Firebase")
                    
            except Exception as e:
                print(f"Error enviando resultados finales a Firebase: {e}")
    
def fetch_historical_data(controller):
    """Obtiene datos históricos de Firebase para análisis offline"""
    print("Obteniendo datos históricos de Firebase...")
    try:
        # Obtener los últimos 200 registros de sensores
        sensor_data = controller.firebase_get("sensores", "?orderBy=\"timestamp\"&limitToLast=200")
        
        if sensor_data and isinstance(sensor_data, dict):
            # Convertir a listas para análisis
            timestamps = []
            values = []
            datetimes = []
            
            for key, value in sensor_data.items():
                if 'ldr_value' in value and 'timestamp' in value:
                    timestamps.append(value['timestamp'])
                    values.append(value.get('ldr_value', 0))
                    datetimes.append(datetime.fromtimestamp(value['timestamp']))
            
            if timestamps:
                # Ordenar por timestamp
                sorted_data = sorted(zip(timestamps, values, datetimes), key=lambda x: x[0])
                timestamps = [x[0] for x in sorted_data]
                values = [x[1] for x in sorted_data]
                datetimes = [x[2] for x in sorted_data]
                
                print(f"Datos obtenidos: {len(timestamps)} registros")
                
                # Guardar datos en CSV
                with open('datos_historicos_ldr.csv', 'w') as f:
                    f.write("timestamp,ldr_value,datetime\n")
                    for t, v, d in zip(timestamps, values, datetimes):
                        f.write(f"{t},{v},{d.strftime('%Y-%m-%d %H:%M:%S')}\n")
                print("Datos guardados en 'datos_historicos_ldr.csv'")
                
                return timestamps, values, datetimes
            else:
                print("No se encontraron datos históricos")
                return None, None, None
        else:
            print("Error al obtener datos o formato incorrecto")
            return None, None, None
    except Exception as e:
        print(f"Error en fetch_historical_data: {e}")
        return None, None, None

def analyze_historical_with_sa(timestamps, values):
    """Analiza datos históricos utilizando el algoritmo de Recocido Simulado"""
    if not timestamps or not values:
        print("No hay datos históricos para analizar")
        return
        
    print("Analizando datos históricos con Recocido Simulado...")
    
    # Parámetros del recocido simulado
    initial_temp = 100
    cooling_rate = 0.95
    min_temp = 0.1
    
    sa_controller = SimpleAnnealingController(initial_temp, cooling_rate, min_temp)
    
    # Usar los datos históricos para simular el paso del tiempo
    for i in range(len(timestamps)):
        # Extraer valor del sensor
        sensor_value = values[i]
        
        # Calcular salida según el recocido simulado
        output = sa_controller.calculate_next_output(sensor_value)
        
        # Registrar para análisis
        sa_controller.sensors_history.append(sensor_value)
        sa_controller.outputs_history.append(output)
        sa_controller.timestamp_history.append(i)
        
    # Análisis final con los datos históricos
    sa_controller.final_analysis()

if __name__ == "__main__":
    # Opciones disponibles para ejecutar
    print("SISTEMA DE CONTROL DE INTENSIDAD LUMÍNICA CON RECOCIDO SIMULADO")
    print("Selecciona una opción:")
    print("1. Ejecutar controlador en tiempo real con Firebase")
    print("2. Analizar datos históricos de Firebase")
    print("3. Ejecutar ambos (análisis histórico y controlador en tiempo real)")
    
    option = input("Opción (1/2/3): ")
    
    controller = SimpleAnnealingController()
    
    if option == '1' or option == '3':
        # Parámetros del recocido simulado
        initial_temp = float(input("Temperatura inicial (predeterminado: 100): ") or "100")
        cooling_rate = float(input("Factor de enfriamiento (0.8-0.99, predeterminado: 0.95): ") or "0.95")
        min_temp = float(input("Temperatura mínima (predeterminado: 0.1): ") or "0.1")
        
        # Duración del análisis
        duration = int(input("Duración del análisis en segundos (predeterminado: 600): ") or "600")
        sample_interval = float(input("Intervalo de muestreo en segundos (predeterminado: 1): ") or "1")
        
        # Crear y ejecutar el controlador
        controller = SimpleAnnealingController(
            initial_temp=initial_temp, 
            cooling_rate=cooling_rate, 
            min_temp=min_temp
        )
        
        # Si seleccionó opción 3, primero hacemos el análisis histórico
        if option == '3':
            timestamps, values, _ = fetch_historical_data(controller)
            if timestamps and values:
                analyze_historical_with_sa(timestamps, values)
            
        # Ejecutar el controlador en tiempo real
        controller.run(duration, sample_interval)
    
    elif option == '2':
        # Solo análisis histórico
        timestamps, values, _ = fetch_historical_data(controller)
        if timestamps and values:
            analyze_historical_with_sa(timestamps, values)
    
    else:
        print("Opción no válida. Saliendo...")
