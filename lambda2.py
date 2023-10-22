""" función de orden superior que recibe una lista de valores enteros y una función
con un parámetro entero y que retorna un booleano.
Imprimir de la lista:

    Los valores múltiplos de 2
    Los valores múltiplos de 3 o de 5
    Los valores mayores o iguales a 50
    Los valores comprendidos entre 1 y 50 o entre 70 y 100.
"""

import random
# Utilizaremos la librería random para hacer mas dinamica la escogencia de numeros


# Abstracción de generación de numeros enteros leatorios dentro de una lista
def numeros_aleatorios(cantidad, min=-1000, max=1000):
    """
    lista de números enteros aleatorios.

    :param cantidad: Número de enteros aleatorios a generar.
    :param min: Valor mínimo del rango para generar los números aleatorios.
    :param max: Valor máximo del rango para generar los números aleatorios.
    :return: Lista de enteros aleatorios.
    """
    return [random.randint(min, max) for x in range(cantidad)]


# Creamos la lista
lista = numeros_aleatorios(10)


# Abstracción para mostrar los ejercicios a realizar
def mostrar_resultado(lista, verify):
    for numero in lista:
        if verify(numero):
            print(numero)


print("Números pares: ")
mostrar_resultado(lista, lambda x: x % 2 == 0)
print("Múltiplos de 3 o de 5: ")
mostrar_resultado(lista, lambda x: x % 3 == 0 or x % 5 == 0)
print("Números mayores o iguales a 50: ")
mostrar_resultado(lista, lambda x: x >= 50)
print("Numeros entre entre 1 y 50 o 70 y 100: ")
mostrar_resultado(lista, lambda x: 1 <= x <= 50 or 70 <= x <= 100)
print("Todos los números de la lista son: ")
mostrar_resultado(lista, lambda x: True)
