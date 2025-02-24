from obtencion_datos import *

if __name__ == "__main__":
    ser = conectar_puerto_serial('/dev/ttyUSB0', 9600) 

    encabezado = ['time','promedio', 'menor', 'mayor', 'mediana', 'moda']
    datos = []

    limite = 50

    i = 0

    try:
        while i != limite:
            linea = leer_linea(ser)
            if linea:
                datos.append(linea)
                print(linea)
                i = i + 1
    except KeyboardInterrupt:
        print("Programa terminado.")
    finally:
        guardar_resultados('potenciometros', encabezado, datos)
        ser.close()
        