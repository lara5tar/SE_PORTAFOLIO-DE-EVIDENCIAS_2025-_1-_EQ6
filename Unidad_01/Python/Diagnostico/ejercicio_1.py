from funciones_auxiliares import vector_aleatorio, valor_objetivo

if __name__ == "__main__":
    vector = vector_aleatorio(5)
    print(f"Vector generado: {vector}")

    print(f"Valor objetivo (f_o): {valor_objetivo(vector)}")
