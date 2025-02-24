import csv

# Archivo CSV de entrada y salida
archivo_entrada = 'temperatura_humedad_1_2.csv'
archivo_salida = 'datos_modificados.csv'

# Leer el archivo CSV y procesar los datos
with open(archivo_entrada, mode='r') as archivo_csv, open(archivo_salida, mode='w', newline='') as archivo_salida_csv:
    lector_csv = csv.reader(archivo_csv)
    escritor_csv = csv.writer(archivo_salida_csv)
    
    # Leer la cabecera
    cabecera = next(lector_csv)
    escritor_csv.writerow(cabecera)  # Escribir la cabecera en el archivo de salida

    
    # Procesar cada fila
    for fila in lector_csv:
        timestamp = fila[0]
        temperatura = float(fila[1]) 
        humedad = float(fila[2])      
        
        # Convertir la temperatura a entero
        temperatura_entero = int(round(temperatura))
        humedad_entero = int(round(humedad))
        
        # Escribir la fila modificada
        escritor_csv.writerow([timestamp, temperatura_entero, humedad_entero])

print(f"Los datos modificados se han guardado en '{archivo_salida}'.")