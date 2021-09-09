import streamlit as st
import pandas as pd
import base64
import plotly.express as px
from streamlit_folium import folium_static 
import folium

# Page Layout
st.set_page_config(layout="wide")

st.title('ETF Portfolio Breakdown')
col1 = st.sidebar
col2, col3 = st.columns((3,3))

col1.header('Info')
col1.markdown("""
This app explores the composition of the holdings within the ETFs used as part of the **Sri Maya Laxmi Ji** investment strategy.
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
""")

# Importing data

markets = pd.read_csv('portfolio_markets.csv')
sectors = pd.read_csv('portfolio_sectors.csv')


markets['Country'] = markets['Country'].replace('Taiwan, Province of China', 'Taiwan', regex= True)
markets['Country'] = markets['Country'].replace('Russian Federation', 'Russia', regex= True)


#etf_grouped = sectors.groupby('ETF')
sector_grouped = sectors.groupby('Sector')

col2.header('Sector breakdown')

# Sector selection
sorted_sector_unique = sorted( sectors['Sector'].unique() )
selected_sector = col2.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = sectors[ (sectors['Sector'].isin(selected_sector)) ]


col2.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
col2.dataframe(df_selected_sector)

# Download VWRL data button

def filedownload(sectors):
    csv = sectors.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="VWRL_sectors.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

sectors_col = sectors['Sector']
allocated_wt = sectors['Allocated Weight']
etf = sectors['ETF']
treemap = px.treemap(
        sectors, 
        path= [sectors_col], 
        values= 'Allocated Weight',
        color= 'Allocated Weight',
        )

col2.plotly_chart(treemap)


col3.header('Markets breakdown')

market_grouped = markets.groupby('Region')

# Region selection
sorted_region_unique = sorted( markets['Region'].unique() )
selected_region = col3.multiselect('Region', sorted_region_unique, sorted_region_unique)

# Filtering data
df_selected_region = markets[ (markets['Region'].isin(selected_region)) ]

col3.write('Data Dimension: ' + str(df_selected_region.shape[0]) + ' rows and ' + str(df_selected_region.shape[1]) + ' columns.')
col3.dataframe(df_selected_region)

# Download VWRL data button

def filedownload(markets):
    csv = markets.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="VWRL_markets.csv">Download CSV File</a>'
    return href

col3.markdown(filedownload(df_selected_region), unsafe_allow_html=True)

# Map

markets_map = markets.copy()
markets_map['radius'] = markets_map['Allocated Weight'].apply(lambda x: x.strip('%'))
markets_map['radius'] = markets_map['radius'].astype(float)
markets_map = markets_map[['Country', 'Region', 'radius']].copy()
markets_map = markets_map.groupby(['Country', 'Region']).sum()
markets_map.reset_index(inplace=True)
#markets_map = markets_map.loc[(markets_map.ETF == "VWRL")]

#col3.dataframe(markets_map)

def filedownload(markets_map):
    csv = markets_map.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="VWRL_markets.csv">Download CSV File</a>'
    return href

#col3.markdown(filedownload(markets_map), unsafe_allow_html=True)

m = folium.Map(location=[0, 0], zoom_start=1, tiles='Stamen', attr='Toner')

#Setting up the world countries data URL
url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
country_shapes = f'{url}/world-countries.json'

#bins = list(markets_map['radius'].quantile([0, 0.25, 0.5, 0.75, 1]))

folium.Choropleth(
    geo_data= country_shapes,
    name='choropleth',
    data=markets_map,
    columns=['Country', 'radius'],
    key_on="feature.properties.name",
    fill_color='YlOrRd',
    line_opacity=.1,
    nan_fill_color='white',
    legend_name='% Allocated Weight',
    bins=9
).add_to(m)

folium.LayerControl().add_to(m)

with col3:
    folium_static(m)

