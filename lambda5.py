"""
Write a Python program to create a function that takes one argument, and that argument will be multiplied
with an unknown given number.
Sample Output:
Double the number of 15 = 30
Triple the number of 15 = 45
Quadruple the number of 15 = 60
Quintuple the number 15 = 75
"""


# We create reusable function that calculates a number
def calculus(calculate, number):
    return calculate(number)


num = int(input("Ingrese el numero que desea multiplicar: "))

x = 1
while x <= 10:
    # In this form we create a lambda function that multiplies a number with a reusable and abstracted function
    multiply = calculus(lambda r: r * x, num)
    print(f"{num} x {x}: {multiply}")
    x += 1
