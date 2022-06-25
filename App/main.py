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

st.set_page_config(page_title='DashBoard - Venta de casas',
                    layout="wide", 
                    page_icon=':eggplant:',  
                    initial_sidebar_state="expanded")


st.title('House Sales in King Country, USA')
st.header('Creado por Emilio Andres Arias M.')

def get_data():
     url = 'https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/kc_house_data.csv'
     return pd.read_csv(url)