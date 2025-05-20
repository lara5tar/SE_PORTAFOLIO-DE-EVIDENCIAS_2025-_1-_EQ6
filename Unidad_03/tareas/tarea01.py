import random

if __name__ == '__main__':

    rangos = [
        (18, 25),      # humedad
        (30, 50),      # temperatura
        (40, 70),     # ruido
        (100, 500)     # iluminacion
    ]

    with open('valores.csv', 'w') as f:
        f.write('humedad,temperatura,ruido,iluminacion\n')
        for _ in range(100):
            humedad = random.randint(rangos[0][0], rangos[0][1])
            temperatura = random.randint(rangos[1][0], rangos[1][1])
            ruido = random.randint(rangos[2][0], rangos[2][1])
            iluminacion = random.randint(rangos[3][0], rangos[3][1])
            f.write(f"{humedad},{temperatura},{ruido},{iluminacion}\n")

