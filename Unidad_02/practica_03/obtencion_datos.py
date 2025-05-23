import serial
import csv
import sys
import time

def conectar_puerto_serial(com, baudios):
    try:
        ser = serial.Serial(com, baudios, timeout=1)  
        print('Se conecto')
        return ser
    except serial.SerialException as e:
        print(f"Error al conectar al puerto serial: {e}")
        sys.exit(1)

def leer_linea(ser):
    try:            
        line = ser.readline().decode('utf-8').strip()
        if line.startswith('f'):
            datos = line.split(',')
            return [obtener_hora()] + [float(valor) for valor in datos[1:]]
    except (ValueError, AttributeError, IndexError) as e:
        print(f"Error al procesar la línea: {e}")
        return None

    
def obtener_hora():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def guardar_resultados(name, encabezados, datos):
    name = f"{name}.csv"
    try:
        with open(name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(encabezados) 
            writer.writerows(datos)
        print(f"Resultados guardados en {name}")
    except IOError as e:
        print(f"Error al guardar el archivo CSV: {e}")


def obtener_datos_csv(name):
    name = name + '.csv'
    datos_time = []
    datos_temperatura = []
    datos_humedad = []
    
    try:
        with open(name, 'r', newline='') as csvfile:
            lector = csv.reader(csvfile)
            next(lector)  # Saltar la fila de encabezados
            for fila in lector:
                datos_time.append(fila[0])
                datos_temperatura.append(float(fila[1]))
                datos_humedad.append(float(fila[2]))
                
        return datos_time, datos_temperatura, datos_humedad
    except FileNotFoundError:
        print(f"Error: El archivo {name} no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None
    
def prender_led(led, ser):
    ser.write((f"1,{led}\n").encode()) 
    
def apagar_led(led, ser):
    ser.write((f"0,{led}\n").encode()) 

def esperar(segundos):
    time.sleep(segundos)

def dia_semana(dia):
    return ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][dia]
