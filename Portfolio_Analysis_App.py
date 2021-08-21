from os import path
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly
import pydeck as pdk 

st.title('ETF Portfolio Breakdown')

st.sidebar.header('Info')
st.sidebar.markdown("""
This app explores the composition of the holdings within the ETFs used as part of the **Sri Maya Laxmi Ji** investment strategy.
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
""")

# Importing data

markets = pd.read_csv('portfolio_markets.csv')
sectors = pd.read_csv('portfolio_sectors.csv')
@st.cache
def load_map_data():
    url = 'https://developers.google.com/public-data/docs/canonical/countries_csv'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

map_data = load_map_data()
markets['Country'] = markets['Country'].replace('Taiwan, Province of China', 'Taiwan', regex= True)
markets['Country'] = markets['Country'].replace('United States of America', 'United States', regex= True)
markets['Country'] = markets['Country'].replace('Russian Federation', 'Russia', regex= True)



left = markets.set_index('Country')
right = map_data.set_index('name')
markets = left.join(right) 
markets = markets.dropna()

#etf_grouped = sectors.groupby('ETF')
sector_grouped = sectors.groupby('Sector')

st.header('Sector breakdown')

# Sector selection
sorted_sector_unique = sorted( sectors['Sector'].unique() )
selected_sector = st.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = sectors[ (sectors['Sector'].isin(selected_sector)) ]


st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# Download VWRL data button

def filedownload(sectors):
    csv = sectors.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="VWRL_sectors.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

sectors_col = sectors['Sector']
allocated_wt = sectors['Allocated Weight']
etf = sectors['ETF']
treemap = px.treemap(
        sectors, 
        path= [sectors_col], 
        values= 'Allocated Weight',
        color= 'Allocated Weight',
        )

st.plotly_chart(treemap)

#better if percentages tho

st.header('Markets breakdown')

market_grouped = markets.groupby('Region')

# Region selection
sorted_region_unique = sorted( markets['Region'].unique() )
selected_region = st.multiselect('Region', sorted_region_unique, sorted_region_unique)

# Filtering data
df_selected_region = markets[ (markets['Region'].isin(selected_region)) ]

st.write('Data Dimension: ' + str(df_selected_region.shape[0]) + ' rows and ' + str(df_selected_region.shape[1]) + ' columns.')
st.dataframe(df_selected_region)

# Download VWRL data button

def filedownload(markets):
    csv = markets.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="VWRL_markets.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_region), unsafe_allow_html=True)

# Map

markets_map = markets.copy()
markets_map['radius'] = markets_map['Allocated Weight'].apply(lambda x: x.strip('%'))
pd.to_numeric(markets_map['radius'])

st.dataframe(markets_map)

def filedownload(markets_map):
    csv = markets_map.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="VWRL_markets.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(markets_map), unsafe_allow_html=True)


view = pdk.ViewState(latitude=0, longitude=0, zoom=0.2,)


mapLayer = pdk.Layer(
        'ScatterplotLayer',
        data=markets_map,
        pickable=True,
        opacity=0.3,
        stroked=True,
        filled=True,
        radius_scale=100,
        radius_min_pixels=10,
        radius_max_pixels=600,
        line_width_min_pixels=1,
        get_position=['longitude', 'latitude'],
        get_radius='radius',
        get_fill_color=[252, 136, 3],
        get_line_color=[255,0,0],
    )

# Create the deck.gl map
r = pdk.Deck(
    layers=[mapLayer],
    initial_view_state=view,
    map_style="mapbox://styles/mapbox/light-v10",
)
st.pydeck_chart(r)