import serial
import csv
import sys
import time

def obtener_hora():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def obtener_fecha():
    return time.strftime('%Y-%m-%d')

def esperar_sec(segundos):
    time.sleep(segundos)

def esperar_min(minutos):
    time.sleep(minutos * 60)

def dia_semana(dia):
    return ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][dia]

class PuertoService:
    def __init__(self, puerto, baudios):
        self.ser = None
        self.conectar_puerto_serial(puerto, baudios)

    def conectar_puerto_serial(self, com, baudios):
        try:
            self.ser = serial.Serial(com, baudios)
        except serial.SerialException as e:
            print(f"Error al conectar al puerto serial: {e}")
            sys.exit(1)
    
    def leer_linea(self):
        try:            
            line = self.ser.readline().decode('utf-8').strip()
            if line.startswith('f'):
                datos = line.split(',')
                return [obtener_hora()] + [float(valor) for valor in datos[1:]]
        except (ValueError, AttributeError, IndexError) as e:
            print(f"Error al procesar la línea: {e}")
            return None
        
    def prender_led(self, led):
        self.ser.write((f"1,{led}\n").encode()) 
        
    def apagar_led(self, led):     
        self.ser.write((f"0,{led}\n").encode()) 

    def cerrar_puerto_serial(self):
        self.ser.close()

    def limpiar_buffer(self):
        self.ser.reset_input_buffer()
    
class EscritorService:
    def __init__(self, name:str, encabezados:list):
        self.name = name
        self.filename = self.name + '_' + obtener_fecha() + '.csv'
        self.encabezados = ['timestamp'] + encabezados

        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(self.encabezados)

    def escribir_linea(self, linea):
        if linea:
            self.writer.writerow(linea)
        else:
            self.writer.writerow([obtener_hora()] + [-1 for _ in range(len(self.encabezados) - 1)])

    def guardar_resultados(self, resultados):
        try:
            with open(self.filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.encabezados)
                writer.writerows(resultados)
            print("Resultados guardados en resultados.csv")
        except IOError as e:
            print(f"Error al guardar el archivo CSV: {e}")

    def obtener_datos_csv(self):
        name = self.name + '.csv'
        datos = []
        
        try:
            with open(name, 'r', newline='') as csvfile:
                lector = csv.reader(csvfile)
                next(lector)  # Saltar la fila de encabezados
                for fila in lector:
                    datos.append([fila[0]] + [float(valor) for valor in fila[1:]])

            return datos
        except FileNotFoundError:
            print(f"Error: El archivo {name} no fue encontrado.")
            return None
        except Exception as e:
            print(f"Error al leer el archivo CSV: {e}")
            return None
    

    def cerrar_archivo(self):
        self.file.close()
