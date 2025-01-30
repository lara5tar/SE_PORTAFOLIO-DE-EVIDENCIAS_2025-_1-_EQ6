import serial

from funciones import guardar_resultados, conectar_puerto_serial, leer_linea

if __name__ == "__main__":
    ser = conectar_puerto_serial('COM5', 115200)
    lista_resultados = []

    try:
        while True:
            try:
                resultado = leer_linea(ser) 
                if resultado:
                    lista_resultados.append(resultado)
            except serial.SerialException as e:
                print(f"Error en la comunicación serial: {e}")
                break

    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")

    finally:
        guardar_resultados('u2-practica', lista_resultados)
        if ser.is_open:
            ser.close()
        print("Programa finalizado.")