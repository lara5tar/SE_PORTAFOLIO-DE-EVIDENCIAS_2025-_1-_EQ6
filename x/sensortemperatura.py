import serial
import csv
import time

# Configuración del puerto serial
ser = serial.Serial('/dev/ttyUSB0', 115200)  # Cambia '/dev/ttyUSB0' por el puerto correcto

# Nombre del archivo CSV
csv_filename = 'temperatura_humedad.csv'

# Crear o abrir el archivo CSV en modo escritura
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Escribir la cabecera del CSV
    writer.writerow(['Timestamp', 'Temperatura', 'Humedad'])

    try:
        while True:
            # Leer línea del puerto serial
            line = ser.readline().decode('utf-8').strip()
            if line.startswith('f'):
                # Suponiendo que la línea tiene el formato "f,temperatura,humedad"
                _, temperatura, humedad = line.split(',')
                # Obtener el timestamp actual
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                # Escribir la línea en el archivo CSV
                writer.writerow([timestamp, temperatura, humedad])
                print(f'{timestamp} - Temperatura: {temperatura} - Humedad: {humedad}')
    except KeyboardInterrupt:
        print("Programa terminado.")
    finally:
        ser.close()
