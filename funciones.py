# Aquí irán las funciones de extracción de ingredientes y de ponderación del ingrediente

'''
El producto final tiene que ser un dict con key:ingrediente, value:puntuación 
Primero extraemos los ingredientes. 
Observamos que la mayoría de ellos vienen seguidos de un 'de' que va seguido de una medida o cantidad. Para simplificar la tarea, 
la función separará las frases por comas.
'''

# def extraccion_ingredientes(df.Ingredientes):

import pandas as pd

def carga_data():
    data = pd.read_csv("data/recetas.csv")
    return data