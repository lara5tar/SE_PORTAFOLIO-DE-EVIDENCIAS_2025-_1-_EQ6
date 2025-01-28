from funciones_auxiliares import vector_aleatorio, valor_objetivo, get_vectores_random

if __name__ == "__main__":

    V = [vector_aleatorio(5) for _ in range(3)]
    
    print(V)

    v1, v2 = get_vectores_random(V, 2)


    print(v1)
    print(v2)

    fo_v1 = valor_objetivo(v1)

    fo_v2 = valor_objetivo(v2)

    print(fo_v1)
    print(fo_v2)


    if fo_v1 < fo_v2:
        mejor = v1
    else:
        mejor = v2

    print(mejor)
