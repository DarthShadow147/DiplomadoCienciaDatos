import json
import folium
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

from PIL                      import Image
from plotly                   import express as px
from folium.plugins           import MarkerCluster
from streamlit_folium         import folium_static
from matplotlib.pyplot        import figimage
from distutils.fancy_getopt   import OptionDummy

st.set_page_config(page_title='Dashboard - Venta de casas',
                    layout="wide", 
                    page_icon=':eggplant:',  
                    initial_sidebar_state="expanded")


st.title('Datos en inmobiliarios en King Country, USA')
st.write('#### Creado por Emilio Andres Arias M.')

def get_data():
     url = 'https://raw.githubusercontent.com/DarthShadow147/DiplomadoCienciaDatos/master/App/DataAccess/kc_house_data.csv'
     return pd.read_csv(url)

data = get_data()
data_ref = data.copy()

st.sidebar.markdown("# Parámetros de búsqueda")

### Creacion y transformacion de datos
data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d').dt.date
data['yr_built']= pd.to_datetime(data['yr_built'], format = '%Y').dt.year

#Creacion de columna "house_age"
data['house_age'] = 'NA'
## Se llena columna con dato 'new_house' para casas con fechas siguientes al año 1990
data.loc[data['yr_built']>1990,'house_age'] = 'new_house' 
## Se llena columna con dato 'old_house' para casas con fechas anteriores al año 1990
data.loc[data['yr_built']<1990,'house_age'] = 'old_house'

## astype convierte un objeto de pandas a otro tipo, en este caso a un string
data['zipcode'] = data['zipcode'].astype(str)

data.loc[data['yr_built']>=1990,'house_age'] = 'new_house' 
data.loc[data['yr_built']<1990,'house_age'] = 'old_house'

## Conversion de datos originales 'Bedrooms' a 'Dormitory_type'
data.loc[data['bedrooms']<=1, 'dormitory_type'] = 'studio'
data.loc[data['bedrooms']==2, 'dormitory_type'] = 'apartment'
data.loc[data['bedrooms']>2, 'dormitory_type'] = 'house'

## Conversion de datos originales 'Condition' a 'Condition_Type'
data.loc[data['condition']<=2, 'condition_type'] = 'bad'
data.loc[data['condition'].isin([3,4]), 'condition_type'] = 'regular'
data.loc[data['condition']== 5, 'condition_type'] = 'good'
### Fin de Creacion y transformacion de datos

### Filtros en el sidebar
data['price_tier'] = data['price'].apply(lambda x: 'Primer cuartil' if x <= 321950 else
                                                   'Segundo cuartil' if (x > 321950) & (x <= 450000) else
                                                   'Tercer cuartil' if (x > 450000) & (x <= 645000) else
                                                   'Cuarto cuartil')

data['price/sqft'] = data['price']/data['sqft_living']

tier = st.multiselect(
     'Cuartil de precios',
    list(data['price_tier'].unique()),
     list(data['price_tier'].unique()))

enableZipCode = st.checkbox('Zip Code')
enableBedrooms = st.checkbox('Habitaciones')

if enableZipCode:
    zipcod = st.sidebar.multiselect(
    'Códigos postales',
    list(sorted(set(data['zipcode']))),
    list(sorted(set(data['zipcode']))))
data = data[(data['price_tier'].isin(tier))&(data['zipcode'].isin(zipcod))]
st.subheader('Filtros adicionales (Opcionales)')


if enableBedrooms:
    if data['bedrooms'].min() < data['bedrooms'].max():
        min_habs, max_habs = st.sidebar.select_slider(
        'Número de Habitaciones',
        options=list(sorted(set(data['bedrooms']))),
        value=(data['bedrooms'].min(),data['bedrooms'].max()))
        data = data[(data['bedrooms']>= min_habs)&(data['bedrooms']<= max_habs)]
    else:
          st.markdown("""El filtro **Habitaciones** no es aplicable para la selección actual de valores""")





### Fin filtros en sidebar