import random

def vector_aleatorio( n):
    return [random.randint(1, 5) for _ in range(n)]

def valor_objetivo(vector):
    return sum(x**2 for x in vector)

def funcion_objetivo(vector):
  return sum(vector)

def get_vectores_random(V, n):
    return random.sample(V, n)