from manager import *

if __name__ == "__main__":
    registros_totales = 144
    contador_registros = 0

    puerto = PuertoService(puerto='/dev/ttyUSB0', baudios=115200)
    escritor = EscritorService(name='temperatura_humedad', encabezados=['temperatura', 'humedad'])

    try:
        while contador_registros < registros_totales:
            linea = puerto.leer_linea()

            escritor.escribir_linea(linea)

            contador_registros += 1

            print(f"{contador_registros} / {registros_totales}")

            # esperar_min(5)
            esperar_sec(5)

            puerto.limpiar_buffer()
    except serial.SerialException as e:
        print(f"Error al leer del puerto serial: {e}")
    except KeyboardInterrupt:
        print("Programa terminado manualmente.")
    finally:
        puerto.cerrar_puerto_serial()
        escritor.cerrar_archivo()
    
    print(f"Se han obtenido {contador_registros} registros.")
    print(f"Resultados guardados en {escritor.filename}")

