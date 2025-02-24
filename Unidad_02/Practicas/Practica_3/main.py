import serial

from funciones import *

if __name__ == "__main__":
    ser = conectar_puerto_serial('COM5', 115200)
    lista_resultados = []

    limite = 100
    contador = 0


    try:
        while contador < limite:
            try:
                resultado = leer_linea(ser) 
                if resultado:
                    lista_resultados.append(resultado)
                    contador += 1
            except serial.SerialException as e:
                print(f"Error en la comunicación serial: {e}")
                break

    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")

    finally:
        guardar_resultados('U1_P3', lista_resultados)
        if ser.is_open:
            ser.close()
        print("Programa finalizado.")