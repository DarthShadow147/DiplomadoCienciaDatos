import geopandas
import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import seaborn as sns

st.set_page_config(layout='wide')

@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)
    data_no_outlier = data.drop(15870)
    data_clean = data_no_outlier.drop_duplicates(subset = ['id'], keep = 'last')
    data_clean['date'] = pd.to_datetime(data_clean['date'], format = '%Y-%m-%d')

    return data_clean

@st.cache(allow_output_mutation=True)
def data_transform(data):

    data['month'] = data['date'].dt.month
    data['year'] = data['date'].dt.year

    # Creating column with season info
    data['season'] = data['month'].apply(lambda x: 'spring' if (x >=3) & (x<=5) else 
                                                   'summer' if (x >=  6) & (x <= 8) else
                                                   'fall' if (x >= 9 ) & (x <= 11) else
                                                   'winter')
    # Creating columns
    data['condition_binary'] = data['condition'].apply(lambda condition: 'good' if condition > 2 else 'bad') 
    data['waterfront_binary'] = data['waterfront'].apply(lambda wf: 'yes' if wf == 1 else 'no') 
    data['view_quality'] = data['view'].apply(lambda view: 'good' if view > 2 else 'bad')
    data['basement'] = data['sqft_basement'].apply(lambda sqft: 'yes' if sqft > 0 else 'no')
    data['lot_size'] = data['sqft_lot'].apply(lambda sqft: 'large' if sqft > 7618 else 'small')
    data['construction'] = data['yr_built'].apply(lambda date: '>1955' if date > 1955 else '<1955')
    data['nbh_lot_size'] = data['sqft_lot15'].apply(lambda sqft: 'large' if sqft > 7620 else 'small')
    data['inside_size'] = data['sqft_living'].apply(lambda sqft: 'large' if sqft > 1910 else 'small')
    data['nbh_inside_size'] = data['sqft_living15'].apply(lambda sqft: 'large' if sqft > 1840 else 'small')
    return data

@st.cache(allow_output_mutation=True)
def data_load_purchase(data):
    ## To buy or not to buy
    median_price = data[['price','zipcode', 'waterfront']].groupby(['zipcode','waterfront']).median('price').reset_index()
    opportunities = pd.merge(data, median_price, on = ['zipcode','waterfront'], how ='inner')

    status = []
    for i in range(len(opportunities)):
        if (opportunities.loc[i,'price_x'] < opportunities.loc[i,'price_y']) and (opportunities.loc[i,'condition'] > 2):
            status.append('Buy')
        else:
            status.append("Don't Buy")

    opportunities['status'] = status
    opportunities = opportunities.rename(columns = {'price_x' : 'price'}) 

    return opportunities

@st.cache(allow_output_mutation=True)
def data_load_season(data):
    ## When to buy?
    # Subset only the ones to be purchased
    purchased = data[data['status'] == 'Buy' ]
    #purchased = purchased.rename(columns = {'price_x' : 'price'}) 
    purchased = purchased.drop('price_y', axis = 1)

    # group the purchased houses by zipcode, waterfront, season and take the mean - This will see if season interferes.
    purchased_median = purchased[['price','zipcode', 'waterfront','season']].groupby(['zipcode','waterfront','season']).median('price').reset_index()

    # Merges with the purchased data - prince_y is the merged price by season
    season_purchased = pd.merge(purchased_median, purchased, on = ['zipcode','waterfront','season'], how ='inner')
    season_purchased = season_purchased.rename(columns = {'price_x' : 'price_by_season', 'price_y': 'buying_price'}) 

    # Determining the profit
    profit = []
    for i in range(len(season_purchased)):
        if (season_purchased.loc[i,'buying_price'] < season_purchased.loc[i,'price_by_season']) and (season_purchased.loc[i,'condition'] > 2):
            profit.append(0.3)
        else:
            profit.append(0.1)

    season_purchased['profit_margin'] = profit

    # Calculating selling price
    selling_price = []
    for i in range(len(season_purchased)):
        sell = season_purchased.loc[i,'buying_price']*season_purchased.loc[i,'profit_margin'] + season_purchased.loc[i,'buying_price']
        selling_price.append(sell)

    season_purchased['selling_price'] = selling_price

    season_opportunities = season_purchased[['id','zipcode','buying_price','selling_price','profit_margin','condition_binary', 'waterfront_binary', 'view_quality', 'basement', 'bathrooms','bedrooms', 'season']]

    return season_opportunities

@st.cache(allow_output_mutation=True)
def map_opportunities(data):
    fig = px.scatter_mapbox(
    data,
    lat = 'lat',
    lon = 'long',
    color = 'status', 
    size = 'price',
    color_continuous_scale = px.colors.cyclical.IceFire,
    size_max = 15,
    zoom = 10)

    fig.update_layout(mapbox_style = 'open-street-map')
    fig.update_layout(height=600, margin = {'r':0, 't':0, 'l':0, 'b':0})

    #place it in the middle of the page

    return fig 

@st.cache(allow_output_mutation=True)
def hypothesis_12(data):
    h1_data = data[['price', 'waterfront_binary']].groupby('waterfront_binary').mean('price').reset_index()
    h1 = px.bar(h1_data,y = 'price', x = 'waterfront_binary', color = 'waterfront_binary', 
                template = 'simple_white', labels = {"waterfront_binary": 'Waterfront'},
                title = 'Waterfront Houses are more expensive, in average')

    h1.update_layout(showlegend = False)
    
    h2_data = data[['price', 'construction']].groupby('construction').mean('price').reset_index()
    h2 = px.bar(h2_data,y = 'price', x = 'construction', color = 'construction', 
                template = 'simple_white', labels = {"construction": 'Construction Year'},
                title = 'Year of construction does not directly interfere in house prices')
    
    h2.update_layout(showlegend = False)

    return h1, h2

@st.cache(allow_output_mutation=True)
def hypothesis_34(data):
    h3_data = data[['price', 'basement']].groupby('basement').mean('price').reset_index()
    h3 = px.bar(h3_data,y = 'price', x = 'basement', color = 'basement', 
                template = 'simple_white', labels = {"basement": 'Houses With Basement'},
                title = 'Houses with basements are 30% more expensive, in average')
    
    h3.update_layout(showlegend = False)
    
    h4_data = data[['price', 'condition']].groupby('condition').mean('price').reset_index()
    h4 = px.bar(h4_data, y = 'price', x = 'condition', 
                template = 'simple_white', labels = {"condition": 'House Condition'},
                title = 'Houses in condition 3 or better do not have significant difference in price')
    
    h4.update_layout(showlegend = False)   
    
    return h3, h4

@st.cache(allow_output_mutation=True)
def hypothesis_56(data):
    h5_data = data[['condition_binary', 'view_quality', 'price']].groupby(['condition_binary', 'view_quality']).mean('price').reset_index()
    condition_view = h5_data[h5_data.view_quality == 'good']

    h5 = px.bar(condition_view, x='condition_binary' ,y='price', color ='condition_binary', 
                template = 'simple_white', labels = {"condition_binary": 'House Condition'},
                title = 'House view interferes more in price than condition (see .ipynb file)')

    h5.update_layout(showlegend = False)   

    h6_data = data [['price', 'view_quality']].groupby('view_quality').mean('price').reset_index()
    h6 = px.bar(h6_data,x='view_quality',y='price', color='view_quality', 
                template = 'simple_white',labels = {'view_quality': 'House view'},
                title = 'Houses with a good view are 50% more expensive, in average')

    h6.update_layout(showlegend = False)
    
    return h5, h6 

@st.cache(allow_output_mutation=True)
def hypothesis_78(data):

    h7_data = data[['price','lot_size', 'nbh_lot_size']].groupby(['lot_size','nbh_lot_size']).mean('price').reset_index()
    h7 = px.bar(h7_data, x=h7_data.loc[2:3,'nbh_lot_size'],y=h7_data.loc[2:3,'price'], color= h7_data.loc[2:3,'nbh_lot_size'],
                template = 'simple_white', labels = {'x': 'Neighboorhood Lot Size (15 closer houses)'},
                title = 'No neighboordhood effect for lot size')
    
    h7.update_layout(showlegend = False)   


    h8_data = data[['price','inside_size', 'nbh_inside_size']].groupby(['inside_size','nbh_inside_size']).mean('price').reset_index()
    h8 = px.bar(h8_data,x=h8_data.loc[2:3,'nbh_inside_size'],y=h8_data.loc[2:3,'price'], color = h8_data.loc[2:3,'nbh_inside_size'],
                template = 'simple_white', labels = {'x': 'Neighboorhood interior size'},
                title = 'Small neighboordhood effect for interior house sizes')

    h8.update_layout(showlegend = False)   

    return h7,h8

@st.cache(allow_output_mutation=True)
def hypothesis_910(data):

    yoy = data[['price', 'year']].groupby('year').sum('price').reset_index()
    yoy['year'] = yoy['year'].astype(str)
    h9 = px.bar(yoy, y='price',x='year',template = 'simple_white', 
                labels = {'year': 'Year'}, color = 'year',
                title = 'Total price for all houses dropped from 2014 to 2015')
    
    h9.update_layout(showlegend = False)   


    mom = data[['month', 'price', 'bathrooms']].groupby(['month', 'bathrooms']).sum('price').reset_index()
    mom_bath = mom[mom.bathrooms == 3] 
    h10 = px.line(mom_bath, y='price', x= 'month', 
                  template = 'simple_white', labels = {'month': 'Month'},
                  title = 'Months with lower prices were from November to February')

    h10.update_layout(showlegend = False)   

    
    return h9, h10



if __name__ == '__main__':
    
    # Title and description
    st.title('House Rocket Company - Insights')
    st.markdown('This app was built based on a analysis made with the Kings County Dataset from Kaggle, based on the instructions from a post from the "[Seja um Data Scientist]"(https://sejaumdatascientist.com/) blog. The code is hosted on [this](https://github.com/ElisaRMA) GitHub repository.')
    st.markdown('House Rocket is a company based on buying, renovating and selling real estate. The main bottleneck, however, is how to select the best real estate opportunities in order to increase the profit. The best case scenario would be to buy good houses, at good conditions and locations, at a low cost to sell them at a higher price.') 
    st.markdown('The business questions/problems to be solved are:')
    st.markdown('1. Which houses the company should buy and at which price?')
    st.markdown('2. Once bought, when should these houses be sold and at which profit margin?')
        
    data = get_data('./datasets/kc_house_data.csv')

    #titles, texts, etc. 
    data_processed = data_transform(data)
    opportunities = data_load_purchase(data_processed)
    season_opportunities = data_load_season(opportunities)

    # Map 
    st.header('Real State Opportunities')
    st.write('In the map below, the available houses were separated into two classes. Blue points represent good investment opportunities, while red dots represent houses that do not offer an attractive bargain. The dataset with the houses classified as good opportunities is available in the next session')
    st.write('If you wish to filter the map, click of the desired category on legend at the right side of the map.')
    
    fig = map_opportunities(opportunities)
    st.plotly_chart(fig)

    st.markdown('This dataset indicated which houses should be purchased based on the data analysis performed. Select the informations you with to see in the dropdown below')
    
    column_selector = st.multiselect('Filter the informations you with to see:', season_opportunities.columns.tolist())

    if column_selector == []:
        dataset = season_opportunities
    else:
        dataset = season_opportunities[column_selector]

    st.write(dataset)

    st.write('If you wish to see all available houses and its attributes check the box below')

    display_db = st.checkbox('Display all houses available.')

    if display_db:
        st.subheader('All available houses')
        st.write(data_processed)


    st.markdown("<h1 style='text-align: center;'>Testing Business Hypothesis</h1>", unsafe_allow_html=True)
    
    h1, h2 = hypothesis_12(data_processed)
    h3, h4 = hypothesis_34(data_processed)
    h5, h6 = hypothesis_56(data_processed)
    h7, h8 = hypothesis_78(data_processed)
    h9, h10 = hypothesis_910(data_processed)

    # H1 and H2
    c1,c2 = st.columns(2)
    
    c1.plotly_chart (h1, use_container_width = True)
    c2.plotly_chart(h2, use_container_width = True)

    # H3, H4 
    c3,c4 = st.columns(2)
    c3.plotly_chart(h3, use_container_width = True)
    c4.plotly_chart(h4, use_container_width = True)

    # H5 and H6 
    c5,c6 = st.columns(2)
    c5.plotly_chart (h5, use_container_width = True)
    c6.plotly_chart(h6, use_container_width = True)

    # H7 and H8 
    c7,c8 = st.columns(2)
    c7.plotly_chart (h7, use_container_width = True)
    c8.plotly_chart(h8, use_container_width = True)

    
    # H9 and H10 
    c9,c10 = st.columns(2)
    c9.plotly_chart (h9, use_container_width = True)
    c10.plotly_chart(h10, use_container_width = True)