from obtencion_datos import *
from funciones import *

if __name__ == "__main__":
    ser = conectar_puerto_serial('/dev/ttyUSB0', 9500) 

    # times, temperaturas, humedad = obtener_datos_csv('temperatura_humedad')

    # print(calc_suavizado_exponencial(convertir_lista(temperaturas), 0.7))

    dia = 0

    while True:
        if dia == 0:
            linea = leer_linea(ser)
            prender_led(5, ser)
            apagar_led(5, ser)
            