import streamlit as st
import string
import regex as re
import numpy as np
import pandas as pd
pd.set_option('display.max_colwidth', -1) #para no limitar ancho de la columna, de momento no funciona

from pytrends.request import TrendReq
pytrend = TrendReq()
    
st.sidebar.title('Selecciona tus ingredientes favoritos!')
df = pd.read_csv('data/recetasfaciles.csv')
dfingredientes = pd.read_csv('data/ingredientes.csv')
dfmilista = pd.read_csv('data/milista.csv')
listaingredientes = dfingredientes.Ingrediente.tolist()


#Con este string conseguimos un desplegable que vaya de la A a la Z.
misletras = list(string.ascii_uppercase)
primeraletra = st.sidebar.selectbox('Selecciona la primera letra del ingrediente que quieras buscar:', misletras)


ingredientesconesaletra = []
for ingrediente in listaingredientes:
    if re.findall(rf"^{primeraletra.lower()}+", str(ingrediente)):
        ingredientesconesaletra.append(ingrediente)

youringredients = st.sidebar.selectbox('Elige ahora el ingrediente o ingredientes que empiezan con...' + primeraletra, ingredientesconesaletra)   
    

if st.sidebar.button('Añadir ingrediente a mi lista'):
    #Guardamos los ingredientes que vamos añadiendo en un dataframe.
    dfmilista.loc[len(dfmilista), ['Mi lista']] = youringredients        
    dfmilista.to_csv('data/milista.csv')
    #Rehacemos el dataframe para que solo contenga ingredientes diferentes, que no haya repetidos.
    dfmilista = pd.DataFrame(data=dfmilista['Mi lista'].unique(), columns=['Mi lista'])
    #Le pedimos que empiece con índice 1 para que al mostrar la lista quede mejor.
    dfmilista.index = np.arange(1,len(dfmilista)+1)  
    #Mostramos la lista de ingredientes que llevamos seleccionados en streamlit.
    st.sidebar.dataframe(dfmilista)
    #Botón para buscar las recetas con los ingredientes de la lista.
if st.sidebar.button('Buscar recetas con estos ingredientes'):
    ingredientes = dfmilista['Mi lista']
    #Ahora buscaremos las recetas que tengan esos ingredientes en mi lista.
    recetas = []    
    for i in range(len(df)):
        cuenta = 0
        for miingrediente in ingredientes:            
            if miingrediente in df.loc[i, 'Ingredientes']:               
                cuenta +=1 
        if cuenta == len(ingredientes):            
            recetas.append(df.loc[i, ['Nombre de la receta', 'Ingredientes', 'Link de la receta']])
    #Limpiamos las recetas si tienen puntos.
    #Porque suelen venir seguidas de comentarios o traducciones.
    for receta in recetas:
        if len(receta[0].split('.'))>1:
            receta[0] = receta[0].split('.')[0]
    if len(recetas) > 0:
        dfencontradas = pd.DataFrame(data=recetas, columns=['Nombre de la receta', 'Link de la receta'])
        dfencontradas.to_csv('data/encontradas.csv', encoding ='utf-8-sig')
        st.write('Con: ' + ", ".join(ingredientes) + ' puedes hacer...')
        st.title('estas fantásticas recetas:')
        #AQUI LLEGA GOOGLE TRENDS
        for i in dfencontradas.index:
            pytrend.build_payload(kw_list=[dfencontradas.loc[i, 'Nombre de la receta']])
            dftrendy = pytrend.interest_by_region()
            #Ordena por score de mayor a menor.
            dftrendy = dftrendy.sort_values(by=dfencontradas.loc[i, 'Nombre de la receta'], axis=0, ascending=False)        
            dfencontradas.loc[i, 'Trendy Score'] = dftrendy.iloc[0][0]
            dfencontradas.loc[i, 'País'] = dftrendy.index[0]
        #Filtramos los resultados para que sólo nos muestre aquellas recetas que tengan un Trendy Score mayor que 0.
        if len(dfencontradas[dfencontradas['Trendy Score']>0]) > 0:
            dfencontradas = dfencontradas[dfencontradas['Trendy Score']>0].sort_values(by='Trendy Score', axis=0, ascending=False)
        #Sin filtrado sería: dfencontradas = dfencontradas.sort_values(by='Trendy Score', axis=0, ascending=False)
        # Reseteamos los índices y los ponemos a partir del 1 para que quede la lista mejor.
        dfencontradas.index = np.arange(1,len(dfencontradas)+1)
        st.dataframe(dfencontradas.drop(columns='Trendy Score'))
    else:
        st.write('Lo sentimos mucho, no hemos encontrado ninguna receta con estos ingredientes!!')
   
   
if st.sidebar.button('Resetear mi lista de ingredientes'):
    dfmilista.drop(columns='Mi lista', inplace = True)
    dfmilista = pd.DataFrame(columns=['Mi lista'])
    dfmilista.to_csv('data/milista.csv')
               

