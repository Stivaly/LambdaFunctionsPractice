"""Desde una función enviar distintas expresiones lambdas que permitan sumar, restar, multiplicar y dividir ."""


# Proceso de abstraccion para ofrecer legibilidad y control de errores con la menor cantidad de código posible
def calculo(num1,num2, calcular):
    try:
        return round(calcular(num1, num2), 2)
    except ZeroDivisionError:
        print("No se puede dividir entre 0")
        return None


# Solicitamos al usuario ingresar 2 numeros a calcular
n1 = int(input("Ingresa el primer numero que deseas calcular"))
n2 = int(input("Ingresa el segundo numero que deseas calcular"))

suma = calculo(n1, n2, lambda nr1, nr2: nr1+nr2)

resta = calculo(n1, n2, lambda nr1, nr2: nr1-nr2)

mult = calculo(n1, n2, lambda nr1, nr2: nr1*nr2)

div = calculo(n1, n2, lambda nr1, nr2: nr1/nr2)

print(f"Suma: {suma}\nResta: {resta}\nMultiplicación: {mult}\nDivisión: {div}")