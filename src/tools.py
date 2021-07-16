import regex as re
import pandas as pd
from pytrends.request import TrendReq
import numpy as np
import streamlit as st


def limpieza(listaingredientes):
    lista_limpia = []
    ingrediente_limpio = ''
    #Recorremos la lista de ingredientes que hemos cogido del dataframe en el punto interior
    for receta in listaingredientes:
        for ingrediente in receta:
            #Limpiamos las cantidades que aparecen al inicio del ingrediente.
            if re.findall("\d", ingrediente.split(' ')[0]) or re.findall("[½¼⅓]", ingrediente.split(' ')[0]):
                ingrediente_limpio = " ".join(ingrediente.split()[1:])
            else:
                ingrediente_limpio = ingrediente
            #Si hay una medida acabada en punto "g. " nos quedamos solo con lo que viene después.
            if re.findall("\.\s", ingrediente_limpio):
                ingrediente_limpio = " ".join(ingrediente.split('. ')[1:])
            #Limpiamos quitando todo lo que vaya entre paréntesis.
            ingrediente_limpio = re.sub(r'\([^())]*\)', '', ingrediente_limpio)
            #En el caso en que haya un comentario después de una coma ", " quitamos todo lo que venga después.

            #Si hay una " y " o una " o " decidimos quedarnos con el primer ingrediente porque a veces salen comentarios o más cosas
            #Ej: canela  y si quieres sabor a cítrico, la ralladura
            if re.findall("\sy\s|\so\s", ingrediente_limpio):            
                ingrediente_limpio = ingrediente_limpio.split(" y ")[0]
                ingrediente_limpio = ingrediente_limpio.split(" o ")[0]            
            #Cuando aparecen ": " los eliminamos por no tratarse de un ingrediente principal de la receta
            if re.findall(":", ingrediente_limpio):
                break        
            #si tiene ' de ' nos quedamos sólo con lo que viene después.
            if re.findall("\sde\s", ingrediente_limpio):            
                ingrediente_limpio = "de ".join(ingrediente_limpio.split('de ')[1:])        
            #Si hay ingredientes vacíos, no los añadimos.
            if ingrediente_limpio =='': break
            lista_limpia.append(ingrediente_limpio.strip(' ').lower())
    return lista_limpia



def buscarrecetas(ingredientes, df):
    recetas = []    
    for i in range(len(df)):
        cuenta = 0
        for miingrediente in ingredientes:            
            if miingrediente in df.loc[i, 'Ingredientes']:               
                cuenta +=1 
        if cuenta == len(ingredientes):            
            recetas.append(df.loc[i, ['Nombre de la receta', 'Ingredientes', 'Link de la receta', 'Link de la imagen']])
    #Limpiamos las recetas si tienen puntos.
    for receta in recetas:
        if len(receta[0].split('.'))>1:
            receta[0] = receta[0].split('.')[0]
    if len(recetas) > 0:
        dfencontradas = pd.DataFrame(data=recetas, columns=['Nombre de la receta', 'Link de la receta', 'Link de la imagen'])
        #dfencontradas['Link de la receta'] = dfencontradas.apply(convert, axis=1)
        dfencontradas.to_csv('data/encontradas.csv', encoding ='utf-8-sig')
        st.subheader('Con ' + ", ".join(ingredientes) + ' puedes hacer...')
        st.header('estas fantásticas recetas:')     
        pytrend = TrendReq()
        for i in dfencontradas.index:
            pytrend.build_payload(kw_list=[dfencontradas.loc[i, 'Nombre de la receta']])
            dftrendy = pytrend.interest_by_region()
            dftrendy = dftrendy.sort_values(by=dfencontradas.loc[i, 'Nombre de la receta'], axis=0, ascending=False)
            dfencontradas.loc[i, 'Trendy Score'] = dftrendy.iloc[0][0]
            if dfencontradas.loc[i, 'Trendy Score'] == 0:                
                dfencontradas.loc[i, 'País'] = ''
            else:
                dfencontradas.loc[i, 'País'] = "Trendy in " + dftrendy.index[0]                
        #Filtramos los resultados para que sólo nos muestre aquellas recetas que tengan un Trendy Score mayor que 0.
        #if len(dfencontradas[dfencontradas['Trendy Score']>0]) > 0:
         #   dfencontradas = dfencontradas[dfencontradas['Trendy Score']>0].sort_values(by='Trendy Score', axis=0, ascending=False)           
        #Sin filtrado sería:
        dfencontradas = dfencontradas.sort_values(by='Trendy Score', axis=0, ascending=False)
        # Reseteamos los índices y los ponemos a partir del 1 para que quede la lista mejor.
        dfencontradas.index = np.arange(1,len(dfencontradas)+1)        
        #st.dataframe(dfencontradas)
        col1, col2, col3 = st.beta_columns(3)
        st.balloons()
        for i in range(1, len(dfencontradas)+1):           
            if i%3==1:
                with col1:
                    st.header("[" + dfencontradas.loc[i, 'Nombre de la receta'] + "](" + dfencontradas.loc[i, 'Link de la receta'] + ")")
                    st.image(dfencontradas.loc[i, 'Link de la imagen'])
                    st.write(dfencontradas.loc[i, 'País'])
            elif i%3==2:
                with col2:
                    st.header("[" + dfencontradas.loc[i, 'Nombre de la receta'] + "](" + dfencontradas.loc[i, 'Link de la receta'] + ")")
                    st.image(dfencontradas.loc[i, 'Link de la imagen'])
                    st.write(dfencontradas.loc[i, 'País'])
            else:
                with col3:
                    st.header("[" + dfencontradas.loc[i, 'Nombre de la receta'] + "](" + dfencontradas.loc[i, 'Link de la receta'] + ")")
                    st.image(dfencontradas.loc[i, 'Link de la imagen'])
                    st.write(dfencontradas.loc[i, 'País'])
    else:
        st.write('Lo sentimos mucho, no hemos encontrado ninguna receta con estos ingredientes!!')