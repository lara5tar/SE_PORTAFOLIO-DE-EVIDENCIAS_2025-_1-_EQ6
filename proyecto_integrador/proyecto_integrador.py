#!/usr/bin/env python3
"""
Proyecto Integrador - Sistema de Control de Intensidad Lumínica
Implementación del algoritmo de Recocido Simulado para control de iluminación con 4 sensores y 4 focos
Basado en datos de Firebase sin conexión directa al ESP32
"""

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from datetime import datetime
import requests
import json
import math
import random as rnd

# Configuración de conexión con Firebase
FIREBASE_URL = "https://embebidos-pi-default-rtdb.firebaseio.com/"

# Objetivo de intensidad lumínica para cada zona (normalizado entre 0-1)
# Podría ajustarse según momento del día o preferencias del usuario
TARGET_INTENSITIES = [0.65, 0.55, 0.70, 0.60]  # Valores objetivo para los 4 sensores

class MultiZoneSimulatedAnnealingController:
    def __init__(self, zones=4, initial_temp=100, cooling_rate=0.95, min_temp=0.1):
        self.name = "Recocido Simulado Multi-zona"
        self.description = "Control basado en Recocido Simulado para múltiples zonas de iluminación"
        self.zones = zones
        self.temperature = initial_temp
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        
        # Estado actual y mejor estado para cada zona
        self.current_outputs = [0.5] * zones  # Comenzamos con salidas medias
        self.best_outputs = [0.5] * zones
        self.best_errors = [float('inf')] * zones
        
        self.iteration = 0
        self.reset_temp_interval = 50  # Reiniciar temperatura cada 50 iteraciones
        
        # Datos para análisis
        self.sensors_history = [[] for _ in range(zones)]
        self.outputs_history = [[] for _ in range(zones)]
        self.temperature_history = []
        self.error_history = [[] for _ in range(zones)]
        self.timestamp_history = []
        self.last_firebase_data = None
    
    def create_neighbor_solutions(self, current_outputs):
        """
        Genera soluciones vecinas para todas las zonas con perturbaciones proporcionales a la temperatura.
        """
        new_outputs = []
        max_change = 0.3 * (self.temperature / self.initial_temp)
        
        for current in current_outputs:
            # Generar un valor vecino con perturbación proporcional a la temperatura
            change = rnd.uniform(-max_change, max_change)
            new_output = current + change
            # Limitar salida entre 0 y 1
            new_output = max(0, min(1, new_output))
            new_outputs.append(new_output)
            
        return new_outputs
    
    def read_sensors_from_firebase(self):
        """Lee los valores de todos los sensores desde Firebase"""
        try:
            # Obtener los últimos datos de los sensores en Firebase
            response = requests.get(f"{FIREBASE_URL}/sensores.json?orderBy=\"timestamp\"&limitToLast=1")
            if response.status_code == 200 and response.json():
                data = next(iter(response.json().values()))
                if 'ldr_value1' in data:
                    self.last_firebase_data = data
                    return [
                        data.get('ldr_value1', 512),
                        data.get('ldr_value2', 512),
                        data.get('ldr_value3', 512),
                        data.get('ldr_value4', 512)
                    ]
            
            # Si no se pueden obtener datos o no están disponibles, usar último valor conocido o simulación
            if self.last_firebase_data and 'ldr_value1' in self.last_firebase_data:
                return [
                    self.last_firebase_data.get('ldr_value1', 512),
                    self.last_firebase_data.get('ldr_value2', 512),
                    self.last_firebase_data.get('ldr_value3', 512),
                    self.last_firebase_data.get('ldr_value4', 512)
                ]
                
        except Exception as e:
            print(f"Error leyendo datos de Firebase: {e}")
            
        # Si no hay datos, simular valores
        # Valores base + ruido + tendencia según hora del día
        hour = datetime.now().hour
        base = 512  # Valor medio
        day_factor = 1.0 if 8 <= hour <= 18 else 0.3  # Día/noche
        
        values = []
        for _ in range(self.zones):
            trend = base * day_factor
            noise = np.random.normal(0, 50)
            values.append(max(0, min(1023, int(trend + noise))))
        
        return values
    
    def send_control_signals_to_firebase(self, outputs):
        """Envía las señales de control para todos los focos a Firebase"""
        try:
            # Convertir valores normalizados (0-1) a PWM (0-255)
            pwm_values = [int(output * 255) for output in outputs]
            
            # Crear payload
            timestamp = int(time.time())
            data = {
                "timestamp": timestamp,
                "heuristic": self.name,
                "temperature": self.temperature,
            }
            
            # Añadir valores de salida para cada zona
            for i, (output, pwm) in enumerate(zip(outputs, pwm_values)):
                data[f"output_value{i+1}"] = output
                data[f"pwm_value{i+1}"] = pwm
            
            # Enviar a Firebase
            response = requests.put(
                f"{FIREBASE_URL}/control/{timestamp}.json",
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Error al enviar control a Firebase: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error en send_control_signals_to_firebase: {e}")
            return False
    
    def log_to_firebase(self, sensor_values, output_values):
        """Registra datos en Firebase para análisis posterior"""
        try:
            # Crear payload
            timestamp = int(time.time())
            
            # Datos base
            data = {
                "timestamp": timestamp,
                "temperature": self.temperature,
                "heuristic": self.name,
            }
            
            # Añadir datos para cada zona
            for i, (sensor, output, target) in enumerate(zip(sensor_values, output_values, TARGET_INTENSITIES)):
                normalized_sensor = sensor / 1023.0
                error = abs(target - normalized_sensor)
                
                data[f"sensor_value{i+1}"] = sensor
                data[f"normalized_value{i+1}"] = normalized_sensor
                data[f"output_value{i+1}"] = output
                data[f"error{i+1}"] = error
                data[f"target{i+1}"] = target
            
            # Enviar a Firebase
            response = requests.put(
                f"{FIREBASE_URL}/recocido_simulado/{timestamp}.json",
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Error al enviar datos a Firebase: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error en log_to_firebase: {e}")
            return False
    
    def calculate_next_outputs(self, sensor_values):
        """
        Implementa el algoritmo de Recocido Simulado para determinar
        las próximas señales de control para los 4 focos
        """
        # Normalizar valores de los sensores
        normalized_sensors = [value / 1023.0 for value in sensor_values]
        
        # Calcular errores actuales respecto a los objetivos
        current_errors = [abs(target - normalized) for target, normalized in zip(TARGET_INTENSITIES, normalized_sensors)]
        
        # Reiniciar temperatura periódicamente para escapar de óptimos locales
        if self.iteration % self.reset_temp_interval == 0 and self.iteration > 0:
            print(f"Reiniciando temperatura a {self.initial_temp} (iteración {self.iteration})")
            self.temperature = self.initial_temp
            
        # Si la temperatura ya es muy baja, usar las mejores soluciones encontradas
        if self.temperature <= self.min_temp:
            outputs = self.best_outputs.copy()
            print(f"Temperatura mínima alcanzada ({self.temperature:.4f}). Usando mejores soluciones encontradas.")
        else:
            # Generar soluciones vecinas
            new_outputs = self.create_neighbor_solutions(self.current_outputs)
            
            # Evaluar si aceptamos los nuevos valores para cada zona
            for i in range(self.zones):
                # Predecir si el cambio nos acerca o aleja del objetivo
                light_too_low = normalized_sensors[i] < TARGET_INTENSITIES[i]
                
                # Estimar si el cambio es favorable
                change_is_favorable = (light_too_low and new_outputs[i] > self.current_outputs[i]) or \
                                     (not light_too_low and new_outputs[i] < self.current_outputs[i])
                
                # Aplica el criterio de aceptación del recocido simulado
                if change_is_favorable:
                    # Si el cambio parece favorable, aceptarlo
                    self.current_outputs[i] = new_outputs[i]
                else:
                    # Si no es favorable, aceptarlo con probabilidad que depende de la temperatura
                    acceptance_probability = math.exp(-current_errors[i] / self.temperature)
                    if rnd.random() < acceptance_probability:
                        self.current_outputs[i] = new_outputs[i]
            
            # Enfriar la temperatura
            self.temperature *= self.cooling_rate
            
            outputs = self.current_outputs.copy()
            
        # Actualizar mejores soluciones si corresponde
        for i in range(self.zones):
            if current_errors[i] < self.best_errors[i]:
                self.best_errors[i] = current_errors[i]
                self.best_outputs[i] = self.current_outputs[i]
                print(f"Nueva mejor solución para zona {i+1}: {self.best_outputs[i]:.4f} (error: {self.best_errors[i]:.4f})")
            
        # Registrar para análisis
        for i in range(self.zones):
            self.error_history[i].append(current_errors[i])
        self.temperature_history.append(self.temperature)
        
        self.iteration += 1
        return outputs
    
    def plot_performance(self):
        """Genera gráficos de rendimiento del algoritmo de Recocido Simulado para todas las zonas"""
        plt.figure(figsize=(15, 15))
        
        # Gráfico de valores de los sensores
        plt.subplot(4, 1, 1)
        for i in range(self.zones):
            plt.plot(self.timestamp_history, self.sensors_history[i], label=f'Sensor {i+1}')
            plt.axhline(y=TARGET_INTENSITIES[i] * 1023, color=f'C{i}', linestyle='--', label=f'Objetivo {i+1}')
        plt.title('Valores de los sensores LDR')
        plt.ylabel('Valor (0-1023)')
        plt.legend()
        
        # Gráfico de señales de control
        plt.subplot(4, 1, 2)
        for i in range(self.zones):
            plt.plot(self.timestamp_history, self.outputs_history[i], label=f'Control {i+1}')
        plt.title('Señales de control enviadas')
        plt.ylabel('Valor (0-1)')
        plt.legend()
        
        # Gráfico de errores
        plt.subplot(4, 1, 3)
        for i in range(self.zones):
            plt.plot(self.timestamp_history, self.error_history[i], label=f'Error {i+1}')
        plt.title('Evolución de errores')
        plt.ylabel('Error')
        plt.legend()
        
        # Gráfico de temperatura
        plt.subplot(4, 1, 4)
        plt.plot(self.timestamp_history, self.temperature_history, 'r-', label='Temperatura')
        plt.title('Evolución de temperatura')
        plt.ylabel('Temperatura')
        plt.xlabel('Tiempo (s)')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('rendimiento_recocido_simulado_multizona.png')
        print("Gráfico de rendimiento guardado como 'rendimiento_recocido_simulado_multizona.png'")
    
    def run(self, duration_seconds=600, sample_interval=1):
        """Ejecuta el controlador durante un periodo de tiempo"""
        print(f"Iniciando controlador de luz con Recocido Simulado para {self.zones} zonas")
        print(f"Duración: {duration_seconds} segundos")
        print(f"Objetivos de intensidad: {[t*100 for t in TARGET_INTENSITIES]}")
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
                
                # Leer sensores desde Firebase
                sensor_values = self.read_sensors_from_firebase()
                normalized_sensors = [v / 1023.0 for v in sensor_values]
                
                # Calcular errores respecto a los objetivos
                errors = [abs(target - normalized) for target, normalized in zip(TARGET_INTENSITIES, normalized_sensors)]
                
                # Calcular salidas según el recocido simulado
                outputs = self.calculate_next_outputs(sensor_values)
                
                # Enviar señales de control a Firebase
                self.send_control_signals_to_firebase(outputs)
                
                # Registrar historial
                for i in range(self.zones):
                    self.sensors_history[i].append(sensor_values[i])
                    self.outputs_history[i].append(outputs[i])
                self.timestamp_history.append(current_time)
                
                # Loggear a Firebase cada 5 iteraciones para no saturar
                if iteration % 5 == 0:
                    self.log_to_firebase(sensor_values, outputs)
                
                # Mostrar progreso
                if iteration % 10 == 0:
                    print(f"[{current_time:.1f}s] Temperatura: {self.temperature:.2f}")
                    for i in range(self.zones):
                        print(f"  Zona {i+1}: Sensor={sensor_values[i]} ({normalized_sensors[i]:.2f}) | "
                              f"Output={outputs[i]:.2f} | Error={errors[i]:.2f}")
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
        """Realiza análisis estadístico final del rendimiento para todas las zonas"""
        print("\n--- ANÁLISIS FINAL DEL RECOCIDO SIMULADO MULTI-ZONA ---")
        
        # Calcular métricas para cada zona
        if all(len(history) > 0 for history in self.error_history):
            overall_avg_error = 0
            overall_mse = 0
            
            # Guardar resultados en un archivo
            with open('resultados_recocido_simulado_multizona.txt', 'w') as f:
                f.write("RESULTADOS DE ANÁLISIS CON RECOCIDO SIMULADO MULTI-ZONA\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duración del análisis: {len(self.timestamp_history)} muestras\n")
                f.write(f"Temperatura inicial: {self.initial_temp}\n")
                f.write(f"Factor de enfriamiento: {self.cooling_rate}\n")
                f.write(f"Temperatura final: {self.temperature:.4f}\n\n")
                
                # Analizar cada zona
                for i in range(self.zones):
                    avg_error = np.mean(self.error_history[i])
                    mse = mean_squared_error([TARGET_INTENSITIES[i]] * len(self.error_history[i]), 
                                           [1 - e for e in self.error_history[i]])
                    
                    overall_avg_error += avg_error
                    overall_mse += mse
                    
                    print(f"Zona {i+1}:")
                    print(f"  Objetivo: {TARGET_INTENSITIES[i]*100:.1f}%")
                    print(f"  Error promedio: {avg_error:.4f}")
                    print(f"  Error cuadrático medio (MSE): {mse:.4f}")
                    print(f"  Mejor salida encontrada: {self.best_outputs[i]:.4f}")
                    print(f"  Mejor error logrado: {self.best_errors[i]:.4f}")
                    
                    f.write(f"ZONA {i+1}:\n")
                    f.write(f"  Objetivo: {TARGET_INTENSITIES[i]*100:.1f}%\n")
                    f.write(f"  Error promedio: {avg_error:.4f}\n")
                    f.write(f"  Error cuadrático medio (MSE): {mse:.4f}\n")
                    f.write(f"  Mejor salida encontrada: {self.best_outputs[i]:.4f}\n")
                    f.write(f"  Mejor error logrado: {self.best_errors[i]:.4f}\n\n")
                
                # Métricas globales
                overall_avg_error /= self.zones
                overall_mse /= self.zones
                
                print(f"\nRendimiento global:")
                print(f"  Error promedio global: {overall_avg_error:.4f}")
                print(f"  MSE global: {overall_mse:.4f}")
                
                f.write(f"RENDIMIENTO GLOBAL:\n")
                f.write(f"  Error promedio global: {overall_avg_error:.4f}\n")
                f.write(f"  MSE global: {overall_mse:.4f}\n")
            
            print(f"\nResultados guardados en 'resultados_recocido_simulado_multizona.txt'")
            
            # Generar gráficos
            self.plot_performance()
            
            # Enviar resultados finales a Firebase
            try:
                final_result = {
                    "timestamp": int(time.time()),
                    "overall_avg_error": overall_avg_error,
                    "overall_mse": overall_mse,
                    "initial_temp": self.initial_temp,
                    "cooling_rate": self.cooling_rate,
                    "final_temp": self.temperature
                }
                
                # Añadir resultados de cada zona
                for i in range(self.zones):
                    zone_prefix = f"zone{i+1}_"
                    final_result[zone_prefix + "target"] = TARGET_INTENSITIES[i]
                    final_result[zone_prefix + "best_output"] = self.best_outputs[i]
                    final_result[zone_prefix + "best_error"] = self.best_errors[i]
                    final_result[zone_prefix + "avg_error"] = np.mean(self.error_history[i])
                    final_result[zone_prefix + "mse"] = mean_squared_error([TARGET_INTENSITIES[i]] * len(self.error_history[i]), 
                                                                           [1 - e for e in self.error_history[i]])
                
                # Enviar a Firebase
                response = requests.put(
                    f"{FIREBASE_URL}/resultados_finales/{int(time.time())}.json",
                    data=json.dumps(final_result)
                )
                
                if response.status_code == 200:
                    print("Resultados finales enviados a Firebase")
                else:
                    print(f"Error al enviar resultados finales a Firebase: {response.status_code}")
                    
            except Exception as e:
                print(f"Error enviando resultados finales a Firebase: {e}")
    
def fetch_historical_data():
    """Obtiene datos históricos de Firebase para análisis offline"""
    print("Obteniendo datos históricos de Firebase...")
    try:
        # Obtener los últimos 200 registros de sensores
        response = requests.get(f"{FIREBASE_URL}/sensores.json?orderBy=\"timestamp\"&limitToLast=200")
        if response.status_code == 200 and response.json():
            sensor_data = response.json()
            
            # Convertir a DataFrame
            data_list = []
            for key, value in sensor_data.items():
                if 'ldr_value1' in value and 'timestamp' in value:
                    data_list.append({
                        'timestamp': value['timestamp'],
                        'ldr_value1': value.get('ldr_value1', 0),
                        'ldr_value2': value.get('ldr_value2', 0),
                        'ldr_value3': value.get('ldr_value3', 0),
                        'ldr_value4': value.get('ldr_value4', 0),
                        'datetime': datetime.fromtimestamp(value['timestamp'])
                    })
                    
            df = pd.DataFrame(data_list)
            if not df.empty:
                df.sort_values('timestamp', inplace=True)
                print(f"Datos obtenidos: {len(df)} registros")
                
                # Guardar datos en CSV
                df.to_csv('datos_historicos_ldr_multizona.csv', index=False)
                print("Datos guardados en 'datos_historicos_ldr_multizona.csv'")
                
                # Generar gráfico de datos históricos
                plt.figure(figsize=(15, 10))
                
                for i in range(1, 5):
                    ldr_col = f'ldr_value{i}'
                    plt.subplot(4, 1, i)
                    plt.plot(df['datetime'], df[ldr_col], label=f'Sensor {i}')
                    plt.axhline(y=TARGET_INTENSITIES[i-1] * 1023, color='r', linestyle='--', label=f'Objetivo {i}')
                    plt.title(f'Datos Históricos del Sensor LDR {i}')
                    plt.ylabel('Valor LDR')
                    if i == 4:
                        plt.xlabel('Fecha/Hora')
                    plt.legend()
                    plt.xticks(rotation=45)
                
                plt.tight_layout()
                plt.savefig('datos_historicos_multizona.png')
                print("Gráfico guardado como 'datos_historicos_multizona.png'")
                
                return df
            else:
                print("No se encontraron datos históricos")
                return None
        else:
            print(f"Error al obtener datos: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error en fetch_historical_data: {e}")
        return None

def analyze_historical_with_sa(data):
    """Analiza datos históricos utilizando el algoritmo de Recocido Simulado"""
    print("Analizando datos históricos con Recocido Simulado...")
    
    # Parámetros del recocido simulado
    initial_temp = 100
    cooling_rate = 0.95
    min_temp = 0.1
    
    zones = 4
    sa_controller = MultiZoneSimulatedAnnealingController(zones, initial_temp, cooling_rate, min_temp)
    
    # Usar los datos históricos para simular el paso del tiempo
    for index, row in data.iterrows():
        # Extraer valores de sensores
        sensor_values = [row[f'ldr_value{i}'] for i in range(1, zones+1)]
        
        # Calcular salidas según el recocido simulado
        outputs = sa_controller.calculate_next_outputs(sensor_values)
        
        # Aquí podrías guardar los resultados en algún lado si es necesario
        
    # Análisis final con los datos históricos
    sa_controller.final_analysis()

if __name__ == "__main__":
    # Opciones disponibles para ejecutar
    print("SISTEMA DE CONTROL DE INTENSIDAD LUMÍNICA CON RECOCIDO SIMULADO (4 ZONAS)")
    print("Selecciona una opción:")
    print("1. Ejecutar controlador en tiempo real con Firebase")
    print("2. Analizar datos históricos de Firebase")
    print("3. Ejecutar ambos (análisis histórico y controlador en tiempo real)")
    
    option = input("Opción (1/2/3): ")
    
    if option == '1' or option == '3':
        # Parámetros del recocido simulado
        initial_temp = float(input("Temperatura inicial (predeterminado: 100): ") or "100")
        cooling_rate = float(input("Factor de enfriamiento (0.8-0.99, predeterminado: 0.95): ") or "0.95")
        min_temp = float(input("Temperatura mínima (predeterminado: 0.1): ") or "0.1")
        
        # Duración del análisis
        duration = int(input("Duración del análisis en segundos (predeterminado: 600): ") or "600")
        sample_interval = float(input("Intervalo de muestreo en segundos (predeterminado: 1): ") or "1")
        
        # Crear y ejecutar el controlador
        controller = MultiZoneSimulatedAnnealingController(
            zones=4,
            initial_temp=initial_temp, 
            cooling_rate=cooling_rate, 
            min_temp=min_temp
        )
        
        # Si seleccionó opción 3, primero hacemos el análisis histórico
        if option == '3':
            data = fetch_historical_data()
            if data is not None and not data.empty:
                analyze_historical_with_sa(data)
            
        # Ejecutar el controlador en tiempo real
        controller.run(duration, sample_interval)
    
    elif option == '2':
        # Solo análisis histórico
        data = fetch_historical_data()
        if data is not None and not data.empty:
            analyze_historical_with_sa(data)
    
    else:
        print("Opción no válida. Saliendo...")
