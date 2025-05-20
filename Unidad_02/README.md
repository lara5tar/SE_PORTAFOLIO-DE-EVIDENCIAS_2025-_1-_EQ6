
# Unidad 02: Sensor Data Processing Project

Este proyecto implementa un sistema que trabaja con datos de sensores (temperatura, humedad, ruido e iluminación), calcula niveles de satisfacción basados en valores predefinidos, y compara diferentes algoritmos de suavizado.

## Características Principales

1. **Procesamiento de sensores**:
   - Configuración de rangos para cada sensor (mínimo y máximo)
   - Distinción entre sensores de tipo minimización y maximización
   - Cálculo de costos por unidad de cambio

2. **Cálculo de satisfacción**:
   - Determinación de satisfacción basada en valores actuales y recomendados
   - Ponderación de cada sensor según su importancia

3. **Cálculo de costos energéticos**:
   - Estimación del costo energético de hacer cambios en valores de sensores
   - Normalización de costos energéticos

4. **Algoritmos de suavizado**:
   - Método 1: `w = (vReal - vSuavizado) / (vReal + vSuavizado)`
   - Método 2: `w = w + x (ValorReal - VaorSuavizado)` donde x es un coeficiente de corrección
   - Comparación visual entre ambos métodos

5. **Función objetivo**:
   - Combinación de satisfacción y costo energético: `Fo = Gs (alfa) + (beta) Ge`
   - Parámetros ajustables alfa y beta (alpha + beta = 1)

## Estructura del Proyecto

- **config.py**: Configuraciones y parámetros del sistema
- **sensor_data.py**: Generación y procesamiento inicial de datos de sensores
- **satisfaction.py**: Cálculos de satisfacción y costos energéticos
- **smoothing.py**: Implementación de algoritmos de suavizado
- **visualization.py**: Visualización de resultados y comparaciones
- **main.py**: Script principal que integra todos los componentes

## Ejecución del Proyecto

Para ejecutar el proyecto, simplemente ejecute el script principal:

```bash
python main.py
```

El script generará datos de sensores, aplicará los algoritmos de suavizado, calculará la satisfacción y costos energéticos, y visualizará los resultados.

## Requisitos

- Python 3.6+
- Numpy
- Matplotlib

## Resultados

El proyecto genera visualizaciones que permiten comparar:
- Los datos originales vs. datos suavizados por ambos métodos
- Los niveles de satisfacción para diferentes escenarios
- La optimización entre satisfacción y ahorro energético

Estas visualizaciones se guardan automáticamente en archivos PNG en el directorio del proyecto.
