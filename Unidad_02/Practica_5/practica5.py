from obtencion_datos import *
from funciones import *

if __name__ == "__main__":
    ser = conectar_puerto_serial('/dev/ttyUSB0', 115200) 

    dia = 0
    totalHoras = 24
    tiempoEspera = 5
    temperaturaLimite = 0

    temperaturasReales = [] 
    temperaturasSuavizadas = []
    alfa = 0.7
   
    try:
        while True:
            if dia_semana(dia) == 'Lunes':
                temperaturasReales.clear()
                for i in range(totalHoras):
                    esperar(tiempoEspera)
                    linea = leer_linea(ser)
                    if linea is None:
                        temperaturasReales.append(-1)
                    else:
                        temperaturasReales.append(linea[2])
                    print(temperaturasReales[i])
                
                print(temperaturasReales)

                print('Ingrese el limite de temperatura: ')
                temperaturaLimite = input()
            else:
                newdatos = []
                if dia_semana(dia) == 'Martes':
                    newdatos = interpolacion_lineal(temperaturasReales)
                else:
                    newdatos = interpolacion_lineal(temperaturasSuavizadas)

                newdatos = identificar_outliers_iqr(newdatos)
                temperaturasSuavizadas = calc_suavizado_exponencial(newdatos, alfa)

                for i in range(totalHoras):
                    esperar(tiempoEspera)
                    print(f"{i} : {temperaturasSuavizadas[i]}")
                    
                    if(temperaturasSuavizadas[i] < float(temperaturaLimite)):
                        apagar_led(5, ser)
                        apagar_led(18, ser)
                        apagar_led(19, ser)
                    else:
                        prender_led(5, ser)
                        prender_led(18, ser)
                        prender_led(19, ser)
                    
            dia = (dia + 1) % 7

    except KeyboardInterrupt:
        print("Programa terminado.")
    finally:
        ser.close()


# practica 5 sin alfina, no toma en cuenta el valor real de lo suavizado
# 
#  paractica 6 con el alfa   