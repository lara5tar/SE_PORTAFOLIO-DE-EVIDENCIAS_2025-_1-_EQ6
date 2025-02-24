import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
# import matplotlib.pyplot as plt

def calc_suavizado_exponencial(serie, alfa):
    # El parámetro alfa controla el peso que se le da a los datos
    # valores cercanos a 1 hacen que los datos recientes tengan más influencia
    # valores cercanos a 0 dan más importancia a los datos antiguos

    serie = convertir_lista(serie)

    new_serie = np.zeros_like(serie) # reserva memoria y rellena con ceros
    new_serie[0] = serie[0]  # El primer valor suavizado es el primer valor de la serie real
    for t in range(1, len(serie)): #calcula los nuevos valores para la serie suavizada
        new_serie[t] = alfa * serie[t] + (1 - alfa) * new_serie[t-1]
    return new_serie

def convertir_lista(lista):
    return np.array(lista)

def arima(datos):
    modelo = ARIMA(datos, order=(1, 2, 1))
    ajuste = modelo.fit()
    pronostico = ajuste.forecat(Steps=1)

    return pronostico

def diferenciacion(datos):
    return np.diff(datos)

def interpolacion_lineal(datos):
    datos = np.array(datos)
    # Encuentra índices de valores faltantes (NaN)
    indices_nan = np.isnan(datos)
    
    # Obtiene índices de valores válidos
    indices_validos = np.where(~indices_nan)[0]
    
    # Realiza la interpolación
    if len(indices_validos) < 2:  # Necesitamos al menos 2 puntos para interpolar
        return datos
        
    return np.interp(
        np.arange(len(datos)),  # índices de todos los puntos
        indices_validos,        # índices de valores conocidos
        datos[indices_validos]  # valores conocidos
    )

def identificar_outliers_iqr(datos):
    datos = np.array(datos)
    
    # Calcular Q1, Q3 e IQR
    Q1 = np.percentile(datos, 25)
    Q3 = np.percentile(datos, 75)
    IQR = Q3 - Q1
    
    # Definir límites
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    
    # Encontrar outliers
    outliers_idx = np.where((datos < limite_inferior) | (datos > limite_superior))[0]
    
    return outliers_idx, (limite_inferior, limite_superior)
