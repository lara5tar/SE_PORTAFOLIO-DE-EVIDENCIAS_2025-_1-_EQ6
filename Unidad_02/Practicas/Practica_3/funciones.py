import serial
import csv
import sys

def funcion_objetivo(vector):
    return sum(vector)

def valor_objetivo(vector):
    return sum(x**2 for x in vector)

def conectar_puerto_serial(com, baudios):
    try:
        return serial.Serial(com, baudios, timeout=1)  
    except serial.SerialException as e:
        print(f"Error al conectar al puerto serial: {e}")
        sys.exit(1)

def leer_linea(ser):
    try:            
        line = ser.readline().decode('utf-8').strip()
        if not line or not (line.startswith('i') and line.endswith('F')):
            return None

        valores_str = line[1:-1].split('-')
        if len(valores_str) != 6:
            return None
        
        return [int(valor) for valor in valores_str]

    except Exception as e:
        print(f"Error: {e}")
        return None
    
def guardar_resultados(name, resultados):
    name = name + '.csv'
    try:
        with open(name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['promedio', 'menor', 'mayor', 'mediana', 'moda' , 'normal'])
            writer.writerows(resultados)
        print("Resultados guardados en resultados.csv")
    except IOError as e:
        print(f"Error al guardar el archivo CSV: {e}")
