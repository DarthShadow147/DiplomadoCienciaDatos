import json
from pickle import NONE
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
from datetime                 import datetime 

st.set_page_config(page_title='Dashboard - Venta de casas',
                    layout="wide", 
                    page_icon=':rocket:',  
                    initial_sidebar_state="expanded")

st.title('Datos en inmobiliarios en King Country, USA')
st.write('#### Creado por Emilio Andres Arias M.')

### Inicio Dataset
@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)

    return data
### Fin Dataset

### Inicio Columna Nueva 
def set_feature(data):
    #add new features
    data['price_m2'] = data['price']/data['sqft_lot']

    return data
### Fin Columna Nueva

### Inicio Parametros de busqueda
def slide_data(data):
    f_zipcode = st.sidebar.multiselect(
    'Código Postal',
    data['zipcode'].unique())

    if (f_zipcode !=[]):
        data = data.loc[data['zipcode'].isin(f_zipcode)]

    elif (f_zipcode != []):
        data = data.loc[data['zipcode'].isin(f_zipcode), :]

    elif (f_zipcode == []):
        data = data.loc[:,]

    else:
        data = data.copy()


    col1, col2 = st.columns((1, 1))

    # Metricas Promedio
    df1 = data[['id','zipcode']].groupby( 'zipcode' ).count().reset_index()
    df2 = data[['price','zipcode']].groupby( 'zipcode').mean().reset_index()
    df3 = data[['sqft_living','zipcode']].groupby( 'zipcode').mean().reset_index()
    df4 = data[['price_m2','zipcode']].groupby( 'zipcode').mean().reset_index()

    # Union
    m1 = pd.merge(df1, df2, on='zipcode', how='inner')
    m2 = pd.merge(m1, df3, on='zipcode', how='inner')
    df = pd.merge(m2, df4, on='zipcode', how='inner')

    df.columns = ['Código Postal', 'Total Casas', 'Precio', 'Pies Cuadrados', 'Precio / M2']

    col1.header('Valores Promedio')
    col1.dataframe(df, height = 600)

    # Estadisticas Desciptivas
    num_attributes = data.select_dtypes(include=['int64', 'float64'])
    media = pd.DataFrame(num_attributes.apply(np.mean))
    mediana = pd.DataFrame(num_attributes.apply(np.median))
    std = pd.DataFrame(num_attributes.apply(np.std))

    max_ = pd.DataFrame(num_attributes.apply(np.max))
    min_ = pd.DataFrame(num_attributes.apply(np.min))

    df1 = pd.concat([max_, min_, media, mediana, std], axis = 1).reset_index()

    df1.columns = ['Atributos', 'Max', 'Min', 'Media', 'Mediana', 'STD']

    col2.header('Análisis descriptivo')
    col2.dataframe(df1, height=600)


    return None

def comercial_data(data):
    st.sidebar.title('Opciones Comerciales')
    st.title('Atributos Comerciales')

    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

    #Filtros
    min_year_built = int(data['yr_built'].min())
    max_year_built = int(data['yr_built'].max())

    st.sidebar.subheader('Año máximo de construcción')
    f_year_built = st.sidebar.slider('Año de construcción', min_year_built,
                                            max_year_built,
                                            min_year_built)

    st.header('Precio promedio por año construido')

    #Selección de datos
    df = data.loc[data['yr_built'] < f_year_built]
    df = df[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

    fig = px.line(df, x='yr_built', y='price')
    st.plotly_chart( fig, use_container_width=True)

    st.header('Precio promedio por día')
    st.sidebar.subheader('Fecha máxima')

    #Filtros
    min_date = datetime.strptime(data['date'].min(), '%Y-%m-%d')
    max_date = datetime.strptime(data['date'].max(), '%Y-%m-%d')

    f_date = st.sidebar.slider('Fecha', min_date, max_date, min_date)

    #Filtrado de Datos
    data['date'] = pd.to_datetime(data['date'])
    df = data.loc[data['date'] < f_date]
    df= df[['date', 'price']].groupby('date').mean().reset_index()

    fig = px.line(df, x='date', y='price')

    st.plotly_chart( fig, use_container_width=True)

    #----------Histograma------------#
    st.header('Distribución de precios')
    st.sidebar.subheader('Precio Máximo')

    #Filtros
    min_price = int(data['price'].min())
    max_price = int(data['price'].max())
    avg_price = int(data['price'].mean())

    #Filtrado de Datos
    f_price = st.sidebar.slider('Precio', min_price, max_price, avg_price)
    df = data.loc[data['price'] < f_price]

    #Grafico
    fig = px.histogram( df, x='price', nbins=50)
    st.plotly_chart(fig, use_container_width=True)
    return None

### Fin Parametros de busqueda



### Llamado de Metodos
path = 'https://raw.githubusercontent.com/DarthShadow147/DiplomadoCienciaDatos/master/App/DataAccess/kc_house_data.csv'
data = get_data(path)

## Parametros
data = set_feature(data)
slide_data(data)
comercial_data(data)

### Fin de Llamado de Metodos