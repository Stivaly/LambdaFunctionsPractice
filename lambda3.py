"""
Función de orden superior que recibe un String y un parámetro de tipo String que retorna un Boolean.

La función debe analizar cada elemento del String llamando a la función que recibe como parámetro,
si retorna True se agrega dicho caracter al String que se retornará.

Definir un String con una cadena cualquiera.
Llamar a la función de orden superior y pasar expresiones lambdas para filtrar y generar otro String
con las siguientes restricciones:
    Solo las vocales
    Solo los caracteres en minúsculas
    Todos los caracteres no alfabéticos
"""


# Definimos función con abstracción para filtrar el string segun las restricciones indicadas
def filter_function(string, function):
    #  Llama a la función function que informará si el caracter analizado debe formar parte del String a retornar.
    stri = ""
    for character in string:
        if function(character):
            stri = stri + character
    return stri


# Verificamos la cadena antes de iniciar el proceso
character = "PruEbA 1, 2, 3 y 4 pARa VeriFicar La fuNción #"
print(f"Cadena original: {character}")
# En este caso lambda considera parte del String a generar solo las vocales minúsculas y mayúsculas
character2 = filter_function(character, lambda char: char in 'aeiouAEIOU')
print(f"Cadena de vocales: {character2}")
# En este caso lambda considera parte del String a generar solo las letras minúsculas
character3 = filter_function(character, lambda char: 'a' <= char <= 'z')
print(f"Cadena de minúsculas: {character3}")
# En este caso lambda considera parte del String a generar solo los caracteres epeciales
character4 = filter_function(character, lambda char: not('a' <= char <= 'z') and not('A' <= char <= 'Z'))
print(f"Cadena de caracteres epeciales: {character4}")
