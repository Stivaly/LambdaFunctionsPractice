"""
Write a Python program to create a lambda function that adds 15 to a given number passed in as an argument, also create
a lambda function that multiplies argument x with argument y and prints the result.
Sample Output:
25
48
"""


# We create reusable function that calculates any args and rounds it by 2
def calculus(calculate, *args):
    return round(calculate(*args), 2)


number_one = int(input("Please enter a integer number that will be add to 15: "))
number_two = int(input("Please enter a integer second number that will be multiply by the 1st number you enter: "))
num_list = [number_one, number_two]


# In this form we create a lambda function that adds 15 with a reusable and abstracted function
add = calculus(lambda *args: sum(args, 15), number_one)


# In this form we create a lambda function that multiplies 2 numbers and give a result
mult = calculus(lambda *args: number_one*number_two, number_one, number_two)


print(f"Added 15, result: {add} \nMultiply {number_one} x {number_two}: {mult}")
