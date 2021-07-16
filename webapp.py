import string
import regex as re
import numpy as np
import pandas as pd
from pytrends.request import TrendReq
import streamlit as st
import src.tools as srct

st.sidebar.title('Selecciona tus ingredientes favoritos!')
df = pd.read_csv('data/recetasfaciles.csv')
dfingredientes = pd.read_csv('data/ingredientes.csv')
dfmilista = pd.read_csv('data/milista.csv')
listaingredientes = dfingredientes.Ingrediente.tolist()
misletras = list(string.ascii_uppercase)
primeraletra = st.sidebar.selectbox('Selecciona la primera letra del ingrediente que quieras buscar:', misletras)

ingredientesconesaletra = []
for ingrediente in listaingredientes:
    if re.findall(rf"^{primeraletra.lower()}+", str(ingrediente)):
        ingredientesconesaletra.append(ingrediente)

youringredients = st.sidebar.selectbox('Elige ahora el ingrediente o ingredientes que empiezan con...' + primeraletra, ingredientesconesaletra) 


def convert(row):
    return '[link]({})'.format(row['Link de la receta'],  row.name)

    
if st.sidebar.button('Añadir ingrediente a mi lista'):
    #Guardamos los ingredientes que vamos añadiendo en un dataframe.
    dfmilista.loc[len(dfmilista), ['Mi lista']] = youringredients        
    dfmilista.to_csv('data/milista.csv')
    #Rehacemos el dataframe para que solo contenga ingredientes diferentes, que no haya repetidos.
    dfmilista = pd.DataFrame(data=dfmilista['Mi lista'].unique(), columns=['Mi lista'])
    #Le pedimos que empiece con índice 1 para que al mostrar la lista quede mejor.
    dfmilista.index = np.arange(1,len(dfmilista)+1)
    dfmilista.to_csv('data/milista.csv')
    #Mostramos la lista de ingredientes que llevamos seleccionados en streamlit.        
    #Botón para buscar las recetas con los ingredientes de la lista.
    st.write(dfmilista)

if st.sidebar.button('Buscar recetas con estos ingredientes'):
    dfencontradas = srct.buscarrecetas(dfmilista['Mi lista'].unique(), df)

    
if st.sidebar.button('Resetear mi lista de ingredientes'):
    dfmilista.drop(columns='Mi lista', inplace = True)
    dfmilista = pd.DataFrame(columns=['Mi lista'])
    dfmilista.to_csv('data/milista.csv')