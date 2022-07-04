import streamlit as st
import pandas as pd
import folium
import numpy as np
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib import gridspec
from datetime import datetime
from ipywidgets import fixed

import matplotlib.ticker as mtick
import ipywidgets as widgets
import plotly.express as px
import seaborn as sns


st.set_page_config( layout = 'wide')

@st.cache( allow_output_mutation=True )
def get_data(path):
    df = pd.read_csv(path)

    return df

path = '/home/user/repos/projeto-insight/kc_house_data.csv'
df = get_data(path)

#=========================================
# ========== Remover duplicatas ==========
#==========================================
def remove_duplicates (df):
    df = df.drop_duplicates(subset = ['id'], keep = 'last')
    return df

#=========================================
# ========== Remover valor erroneo ==========
#==========================================
def remove_value (df):
    df = df.drop(15870)
    return df

def data_overview(df):
    if st.checkbox('Mostre o dataset'):
     st.write(df)

data_overview(df)
#=========================================
# ========== Métricas ==========
#==========================================
#Incluindo somente variáveis numéricas
st.header('Análises descritivas')
atri_num = df.select_dtypes(include = ['int64', 'float64'])
#deletando a coluna 'ID'
atri_num = atri_num.iloc[:, 1: ]
#medidas de tendencia central
df_mean =  pd.DataFrame(atri_num.apply(np.mean)).T
df_median = pd.DataFrame(atri_num.apply(np.median)).T

#medidas de dispersão
df_std = pd.DataFrame(atri_num.apply(np.std)).T
df_min = pd.DataFrame(atri_num.apply(np.min)).T
df_max = pd.DataFrame(atri_num.apply(np.max)).T

#concatenando
est = pd.concat( [df_mean, df_median,  df_std, df_min, df_max ] ).T.reset_index()



#alterando o nome das colunas
est.columns = [ 'atributos','media', 'mediana', 'std', 'min', 'max']

st.dataframe(est)
st.dataframe()
#=========================================
# ========== H1 ==========
#==========================================
st.header('Testando Hipóteses de Negócio')

c1,c2 = st.beta_columns(2)

c1.subheader('Hipótese 1:  Imóveis com vista para a água são em média 30% mais caros')
h1 = df[['price', 'waterfront']].groupby('waterfront').mean().reset_index()
h1['waterfront'] = h1['waterfront'].astype(str)
fig = px.bar(h1, x='price', y = 'waterfront')
c1.plotly_chart(fig, use_container_width= True)

#=========================================
# ========== H2 ==========
#==========================================
c2.subheader('Hipótese 2: Imóveis com data de construção menor que 1955 são em média 50% mais baratos')
df['construcao'] = df['yr_built'].apply(lambda x: '> 1955' if x > 1955
                                                               else '< 1955')

h2 = df[['construcao', 'price']].groupby('construcao').mean().reset_index()

fig2 = px.bar(h2, x='construcao', y = 'price')
c2.plotly_chart(fig2, use_container_width= True)

#=========================================
# ========== H3 ==========
#==========================================
c3,c4 = st.beta_columns(2)

c3.subheader('Hipótese 3: Imóveis sem porão com maior área total são 40% maiores do que imóveis com porão')
df['porao'] = df['sqft_basement'].apply(lambda x: 'nao' if x == 0
                                                  else 'sim')

h3 = df[['porao', 'sqft_lot']].groupby('porao').sum().reset_index()
fig3 = px.bar(h3, x='porao', y = 'sqft_lot')
c3.plotly_chart(fig3, use_container_width= True)

#=========================================
# ========== H4 ==========
#==========================================
c4.subheader('Hipótese 6: Imóveis que nunca foram reformadas são em média 20% mais baratos')
df['renovacao'] = df['yr_renovated'].apply(lambda x: 'sim' if x > 0 else
                                                     'nao'   )

h6 = df[['price', 'renovacao']].groupby('renovacao').mean().reset_index()
fig4 = px.bar(h6, x='renovacao', y = 'price')
c4.plotly_chart(fig4, use_container_width= True)

#=========================================
# ========== H5 ==========
#==========================================
c5, c6 = st.beta_columns(2)

c5.subheader('Hipótese 7: Imóveis em más condições mas com boa vista são 10% mais caros')
h71 = df[df['condition'] == 1]
h7 = h71[['price', 'view']].groupby('view').sum().reset_index()

fig5 = px.bar(h7, x= 'view', y = 'price')
c5.plotly_chart(fig5, use_container_width= True)


#=========================================
# ========== H4 ==========
#==========================================

c6.subheader('Hipótse 8: Imóveis antigos e não renovados são 40% mais baratos')
df['renovacao'] =  df['yr_renovated'].apply(lambda  x: 'sim' if x > 0 else
                                                        'nao')

df['contrucao'] = df['yr_built'].apply(lambda x: 'antigo' if (x < 1951) else
                                               'atual')
h8 = df[df['renovacao'] == 1]
h8 = df[['contrucao', 'price']].groupby('contrucao').sum().reset_index()
fig6 = px.bar(h8, x ='contrucao', y = 'price')
c6.plotly_chart(fig6, use_container_width= True)


#=========================================
# ========== H7 ==========
#==========================================
c7, c8 = st.beta_columns(2)

c7.subheader('Hipótese 7: Imóveis com mais banheiros são em média 5% mais caros')
df['banheiro'] =  df['bathrooms'].apply(lambda x: '0-3' if (x > 0 ) & (x < 3) else
                                                   '3-5' if (x > 3) & (x < 5) else
                                                   '5-8')

h9 = df[['banheiro', 'price']].groupby('banheiro').mean().reset_index()

fig7 = px.bar(h9, x = 'banheiro', y = 'price')
c7.plotly_chart(fig7, use_container_width= True)


#=========================================
# ========== H8 ==========
#==========================================
c8.subheader('Hipótese 8: Imóveis renovados recentemente são 35% mais caros')
df['contrucao'] = df['yr_built'].apply(lambda x: 'antigo' if (x < 1951) else
                                               'atual')

h10 = df[['contrucao', 'price']].groupby('contrucao').mean().reset_index()

fig8 = px.bar(h10, x = 'contrucao', y = 'price')
c8.plotly_chart(fig8, use_container_width= True)

#=========================================
# ========== H9 ==========
#==========================================
st.subheader('Hipótese 9: O crescimento do preço dos imóveis ano após ano (YoY) é de 10% ')
df['date'] = pd.to_datetime(df['date'])

df['mes'] = df['date'].dt.month

h41 = df[['mes', 'price']].groupby('mes').sum().reset_index()
fig41 = px.line(h41, x='mes', y = 'price')

st.plotly_chart(fig41, use_container_width= True)
#=========================================
# ========== 10==========
#==========================================
st.subheader('Hipótese 10: Imóveis com 3 banheiros tem um crescimento mês após mês de 15 %')
h5 = df[(df['bathrooms'] == 3)]

h5 = h5[['mes', 'price']].groupby('mes').sum().reset_index()


fig5 = px.line(h5, x = 'mes', y = 'price')
st.plotly_chart(fig5, x='mes', y='price')

st.header('Questões de Negócio')
st.subheader('Quais são os imóveis que a House Rocket deveria comprar e por qual preço?')
#Respondendo
a = df[['zipcode', 'price']].groupby('zipcode').median().reset_index()
df2 = pd.merge(a, df, on='zipcode', how = 'inner')
df2 = df2.rename(columns = {'price_y' : 'price', 'price_x' : 'price_median'} ) #alterando nome das colunas
#criando coluna
for i, row in df2.iterrows():
    if (row['price_median'] >= row['price']) & (row['condition'] < 3):
        df2.loc[i,'pay'] =  'sim'
    else:
        df2.loc[i, 'pay'] = 'nao'


#Mapa
# mapa = folium.Map(width = 600, height = 400,
#                   location = [df['lat'].mean(),df[ 'long'].mean()],
#                   default_zoom_start=15)
st.title('Mapa de Compra')
comprados = df2[df2['pay'] == 'sim']
mapa = folium.Map(location = [comprados['lat'].mean(), comprados['long'].mean()], zoom_start= 11)
for each in comprados[0:1000].iterrows():
    folium.Marker(
        location = [each[1]['lat'],each[1]['long']],
        clustered_marker = True).add_to(mapa)

folium_static(mapa)