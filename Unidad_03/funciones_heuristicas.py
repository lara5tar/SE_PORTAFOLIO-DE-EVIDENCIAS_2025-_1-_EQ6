import numpy as np

# Valores actuales (Va)
VA = np.array([18, 90, 67, 800])

# Pesos de cada sensor (w)
W = np.array([0.4, 0.2, 0.1, 0.3])

# Valores objetivo propuestos (Vo)
VO_OPCIONES = np.array([
    [21, 41, 76, 666],  # v1
    [23, 42, 78, 797],  # v2
    [20, 60, 50, 777]   # v3
])

# Rangos de los sensores (min, max)
RANGOS = {
    'humedad': (20, 28),      # minimización
    'temperatura': (40, 80),  # minimización
    'ruido': (60, 120),      # minimización
    'iluminacion': (400, 900) # maximización
}

def calcular_satisfaccion_minimizacion(vo, minimo, maximo):

    if vo <= minimo:
        return 1.0
    elif vo >= maximo:
        return 0.0
    else:
        return (maximo - vo) / (maximo - minimo)

def calcular_satisfaccion_maximizacion(vo, minimo, maximo):
    if vo <= minimo:
        return 0.0
    elif vo >= maximo:
        return 1.0
    else:
        return 1 - ((maximo - vo) / (maximo - minimo))

def calcular_utilidad_total(vo):

    satisfacciones = np.zeros(4)
    for i in range(3):
        minimo, maximo = list(RANGOS.values())[i]
        satisfacciones[i] = calcular_satisfaccion_minimizacion(vo[i], minimo, maximo)
    
    # El último es maximización (iluminación)
    minimo, maximo = RANGOS['iluminacion']
    satisfacciones[3] = calcular_satisfaccion_maximizacion(vo[3], minimo, maximo)
    
    # Calcular utilidad total (suma ponderada)
    utilidad = np.sum(satisfacciones * W)
    return utilidad

def evaluar_todas_opciones():
    """
    Evalúa todas las opciones de Vo y retorna la mejor
    """
    utilidades = []
    for vo in VO_OPCIONES:
        utilidad = calcular_utilidad_total(vo)
        utilidades.append(utilidad)
        print(f"Vo: {vo} -> Utilidad: {utilidad:.3f}")
    
    mejor_indice = np.argmax(utilidades)
    return VO_OPCIONES[mejor_indice], utilidades[mejor_indice]

# Ejemplo de uso
if __name__ == "__main__":
    mejor_vo, mejor_utilidad = evaluar_todas_opciones()
    print("\nMejor opción:")
    print(f"Vo: {mejor_vo}")
    print(f"Utilidad: {mejor_utilidad:.3f}")
