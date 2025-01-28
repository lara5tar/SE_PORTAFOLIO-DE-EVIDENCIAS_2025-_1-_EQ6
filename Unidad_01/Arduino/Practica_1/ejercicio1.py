from funciones_auxiliares import funcion_objetivo

import serial
import csv
import sys

# Configurar la conexión serial
try:
    ser = serial.Serial('COM5', 115200, timeout=1)  # Added timeout
except serial.SerialException as e:
    print(f"Error al conectar al puerto serial: {e}")
    sys.exit(1)

if __name__ == "__main__":
    lista_resultados = []

    try:
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:  
                    continue
                
                if line.startswith('i') and line.endswith('F'):
                    valores_str = line[1:-1].split('-')
                    if len(valores_str) != 4:
                        print("Error: Vector incompleto")
                        continue
                                           
                    vector = [int(valor) for valor in valores_str]
                    
                    # Calcular la función objetivo
                    resultado = funcion_objetivo(vector)
                    
                    # Agregar el vector y su resultado a la lista
                    lista_resultados.append((vector, resultado))
                    
                    # Imprimir los resultados en la consola
                    print(f"Vector: {vector}, Función objetivo: {resultado}")

            except (ValueError, UnicodeDecodeError) as e:
                print(f"Error en la lectura de datos: {e}")
            except serial.SerialException as e:
                print(f"Error en la comunicación serial: {e}")
                break

    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")

    finally:
        try:
            # Guardar los resultados en un archivo CSV
            with open('resultados.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Vector', 'Funcion Objetivo'])
                writer.writerows(lista_resultados)
            print("Resultados guardados en resultados.csv")
        except IOError as e:
            print(f"Error al guardar el archivo CSV: {e}")
            
        if ser.is_open:
            ser.close()
