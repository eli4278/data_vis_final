#!/usr/bin/env python
# coding: utf-8

# Read in Data

# In[48]:


import numpy as np
import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb+srv://ndemoura:Password4project@cluster0.ixcjmes.mongodb.net/?retryWrites=true&w=majority")
db = client.europe_cities
collection = db.cities_info
df = pd.DataFrame(list(collection.find()))
df.head()


# Add City Coordinates

# In[49]:


city_coords = {
    "London": (51.51317, -0.1398445),
    "Paris": (48.8629084, 2.3391898),
    "Berlin": (52.519804, 13.394250),
    "Madrid": (40.4168, -3.7038),
    "Rome": (41.9028, 12.4964),
    "Moscow": (55.7558, 37.6176),
    "Athens": (37.9838, 23.7275),
    "Lisbon": (38.7223, -9.1393),
    "Dublin": (53.3498, -6.2603),
    "Amsterdam": (52.3702, 4.8952),
    "Brussels": (50.8503, 4.3517),
    "Vienna": (48.2082, 16.3738),
    "Budapest": (47.4979, 19.0402),
    "Prague": (50.0755, 14.4378),
    "Warsaw": (52.2297, 21.0122),
    "Stockholm": (59.3293, 18.0708),
    "Oslo": (59.9139, 10.7522),
    "Copenhagen": (55.6761, 12.5683),
    "Helsinki": (60.168153, 24.934411),
    "Kiev": (50.4501, 30.5234),
    "Istanbul": (41.0082, 28.9784),
    "Barcelona": (41.3851, 2.1734),
    "Munich": (48.1371, 11.5761),
    "Milan": (45.4642, 9.1905),
    "St. Petersburg": (59.9343, 30.3351),
    "Zurich": (47.3769, 8.5417),
    "Geneva": (46.2044, 6.1432),
    "Belgrade": (44.818872, 20.460151),
    "Bucharest": (44.4323, 26.1063),
    "Sofia": (42.6977, 23.3219),
    "Riga": (56.9496, 24.1052),
    "Tallinn": (59.4370, 24.7536),
    "Vilnius": (54.6892, 25.2797),
    "Reykjavik": (64.1265, -21.8174),
    "Edinburgh": (55.9533, -3.1883),
    "Glasgow": (55.8642, -4.2518),
    "Naples": (40.8522, 14.2681),
    "Minsk": (53.9023, 27.5662),
    "Frankfurt": (50.1109, 8.6821),
    "Cologne": (50.9375, 6.9603),
    "Hamburg": (53.5511, 9.9937),
    "Marseille": (43.2965, 5.3698),
    "Lyon": (45.7485, 4.8467),
    "Valencia": (39.4699, -0.3763),
    "Seville": (37.3886, -5.9823),
    "Gothenburg": (57.7089, 11.9746),
    "Antwerp": (51.2195, 4.4025),
    "Porto": (41.1579, -8.6291)
}

lon = []
lat = []
for i in range(48):
    lon.append(city_coords[df['city'][i]][0])
    lat.append(city_coords[df['city'][i]][1])
df['lon'] = lon
df['lat'] = lat
df.head()


# Clean the data

# In[58]:


df1 = df.iloc[: , 1:]
df1 = df1.drop('walkscore', axis=1)

clIndex = []
for city in df1['cost_of_living']:
    if len(city) > 0:
        clIndex.append(float(city['clInx']))
    else:
        clIndex.append(np.NaN)
df1['cost_of_living'] = clIndex

df1['internet speed mobile'] = pd.to_numeric(df1['internet speed mobile'])
df1['internet speed fixed'] = pd.to_numeric(df1['internet speed fixed'])

df1.head()


# Prototype Map

# In[61]:


import plotly.graph_objects as go

fig = go.Figure(data=go.Scattergeo(
    lat = df1['lon'],
    lon = df1['lat'],
    text = df1['city'],
    mode = 'markers',
    marker = dict(
        size = 8,
        opacity = 0.8,
        reversescale = False,
        autocolorscale = False,
        symbol = 'square',
        line = dict(
            width=1,
            color='rgba(102, 102, 102)'
        ),
        cmin = 62,
        color = df1['walkability'],
        cmax = df1['walkability'].max(),
        colorbar_title="Walkability"
    )
))

fig.update_layout(
    title = 'Europe Cities<br>(Hover for City information)',
    geo_scope='europe',
)
fig.show()


# Transfer Map to Dash

# In[62]:


from dash import Dash, Input, Output, dcc, html

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Digital Nomad Analysis"

app.layout = html.Div([
    html.H4('Best Cities for Digital Nomads in Europe'),
    html.P("Select a category:"),
    dcc.RadioItems(
        id='category',
        options=["walkability", "cost_of_living", "internet speed mobile", "internet speed fixed"],
        value="cost_of_living",
        inline=True
    ),
    dcc.Graph(id="graph"),
])

@app.callback(
    Output("graph", "figure"),
    Input("category", "value"))
def display_map(category):
    fig = go.Figure(data=go.Scattergeo(
        lat = df1['lon'],
        lon = df1['lat'],
        text = df1['city'],
        mode = 'markers',
        marker = dict(
            size = 8,
            opacity = 0.8,
            reversescale = False,
            autocolorscale = False,
            symbol = 'square',
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            cmin = 62,
            color = df1[category],
            cmax = df1[category].max(),
            colorbar_title=category
        )
    ))

    fig.update_layout(
        title = 'Europe Cities<br>(Hover for City information)',
        geo_scope='europe',
    )
    return fig


app.run_server(debug=True)
