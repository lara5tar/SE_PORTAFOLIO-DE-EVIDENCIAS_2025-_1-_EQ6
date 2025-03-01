def satisfaccion_min(x, minimo, maximo):
    return (maximo - x) / (maximo - minimo)

def satisfaccion_max(x, minimo, maximo):
    return 1 - ((maximo - x) / (maximo - minimo))

def calcular_Eo(Va, Vo, Cx):
    return Cx + (Cx * (Va - Vo))

def calcular_Emin(Va, Vmax, Cx):
    return Cx + (Cx * (Va - Vmax))

def calcular_Emax(Va, Vmin, Cx):
    return Cx + (Cx * (Va - Vmin))

def satisfaccion(Eo, Emax, Emin):
    if Emax == Emin:
        return 1.0
    return 1 - ((Emax - Eo) / (Emax - Emin))

if __name__ == '__main__':
    w = [0.4, 0.2, 0.1, 0.3]
    
    Va = [26, 90, 67, 800]  
    
    C = [40, 25, 12, 3]  
    
    Vos = [
        [21, 41, 76, 666],  # v1
        [23, 42, 78, 797],  # v2
        [20, 60, 50, 777]   # v3
    ]

    rangos = [
        (20, 28),      # humedad
        (40, 80),      # temperatura
        (60, 120),     # ruido
        (400, 900)     # iluminacion
    ]

    for i, Vo in enumerate(Vos):
        
        satisfacciones = [
            w[0] * satisfaccion_min(Vo[0], rangos[0][0], rangos[0][1]),
            w[1] * satisfaccion_min(Vo[1], rangos[1][0], rangos[1][1]),
            w[2] * satisfaccion_min(Vo[2], rangos[2][0], rangos[2][1]),
            w[3] * satisfaccion_max(Vo[3], rangos[3][0], rangos[3][1])
        ]
        
        for j in range(4):
            print('-----------------------------------------------')
            Eo = calcular_Eo(Va[j], Vo[j], C[j])
            Emin = calcular_Emin(Va[j], rangos[j][1], C[j])
            Emax = calcular_Emax(Va[j], rangos[j][0], C[j])
            
            print(satisfacciones[j])
            print(Eo)
            print(Emin)
            print(Emax)
            print(f"Satisfacción: {satisfaccion(Eo, Emax, Emin)}")
        print('-----------------------------------------------')
        print(f"Satisfacción total: {sum(satisfacciones)}")
