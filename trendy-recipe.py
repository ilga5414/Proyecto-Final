import streamlit as st
import pandas as pd
import numpy as np
import src.funciones as dat
from PIL import Image
import plotly.express as px 

st.title('The Trendy Recipe')

Image = Image.open("pics/images.jpeg")

st.image(Image)

st.write("""
# Need some help to find recipe inspiration?
## Tell us what you have at home and we will help you out!
""")

# dat es el alias y carga_data es la funcion
datos = dat.carga_data()