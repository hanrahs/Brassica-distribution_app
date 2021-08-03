import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash
from dash.dependencies import Input, Output


app = dash.Dash(__name__)

app = app.server

df = pd.read_csv("data.csv", low_memory=False)


def f(row):
    if row['info'] == 1:
        val = 'GPS'
    elif row['info'] == 2:
        val = 'Detailed Description'
    elif row['info'] == 3:
        val = 'Town or Locality'
    elif row['info'] == 4:
        val = 'Region'
    elif row['info'] == 5:
        val = 'Country'
    elif row['info'] == 7:
        val = 'Former Country'
    else:
        val = 'Unknown'
    return val


df['info_names'] = df.apply(f, axis=1)

# print(df['info_names'])


def g(row):
    if row['SAMPSTAT'] == 100:
        val = 'Wild'
    elif row['SAMPSTAT'] == 110:
        val = 'Natural'
    elif row['SAMPSTAT'] == 120:
        val = 'Semi-natural (wild)'
    elif row['SAMPSTAT'] == 130:
        val = 'Semi-natural (sown)'
    elif row['SAMPSTAT'] == 200:
        val = 'Weedy'
    elif row['SAMPSTAT'] == 300:
        val = 'Traditional Cultivar/Landrace'
    else:
        val = 'Unknown'
    return val


df['sampstat_names'] = df.apply(g, axis=1)

# print(df['sampstat_names'])

# df['baz'] = df.agg(lambda x: f"{x['bar']} is {x['foo']}", axis=1)

df['popup_data'] = df.agg(
    lambda df: f"Country: {df['Country']},  Sampstat: {df['sampstat_names']},  Passport data: {df['info_names']}", axis=1)
# print(df['popup_data'])


def get_data(source_selected, species_selected, info_selected, sampstat_selected):

    df_bdd = df[['ID', 'source', 'GENUS', 'Species', 'Country', 'COLLSITE', 'lat',
                 'lon', 'info', 'Elevation', 'SAMPSTAT', 'COLLSRC', 'info_names', 'sampstat_names', 'popup_data']].copy()

    df_bd = df_bdd.dropna(subset=['lon'])

    df_bd = df_bd[(df_bd['source'].isin(source_selected))
                  & (df_bd['Species'].isin(species_selected))
                  & (df_bd['info'].isin(info_selected))
                  & (df_bd['SAMPSTAT'].isin(sampstat_selected))
                  ].copy()

    # print(df_bd.dtypes)
    # df_bd = pd.to_numeric(df_bd, errors='coerce')
    # print(df_bd)

    dicts = df_bd.to_dict('rows')
    for item in dicts:
        item["tooltip"] = (item["Species"])  # bind tooltip
        item["popup"] = item['popup_data']  # bind popup
    geojson = dlx.dicts_to_geojson(dicts)  # convert to geojson
    geobuf = dlx.geojson_to_geobuf(geojson)  # convert to geobuf
    return geobuf


# set defaults
default_species = ['rapa', 'oleracea']
default_source = ['eurisco']
default_info = [1, 2, 3]
default_sampstat = [100]


# set options

df_bcc = df[['ID', 'source', 'GENUS', 'Species', 'Country', 'COLLSITE', 'lat',
             'lon', 'info', 'Elevation', 'SAMPSTAT', 'COLLSRC']].copy()  # drop irrelevant columns

# print(df_bdd.dtypes)
df_bcc = df_bcc[df_bcc['info'] > 0.1].copy()

species_options = [{'label': x, 'value': x, 'disabled': False}
                   for x in df_bcc['Species'].unique()]

# info_options = [{'label': x, 'value': x, 'disabled': False}
#                 for x in df_bcc['info'].unique()]

source_options = [{'label': x, 'value': x, 'disabled': False}
                  for x in df_bcc['source'].unique()]

sampstat_options = [{'label': x, 'value': x, 'disabled': False}
                    for x in df_bcc['SAMPSTAT'].unique()]


# drawing points

geojson = dl.GeoJSON(data=get_data(default_source, default_species, default_info, default_sampstat), id="geojson", format="geobuf",
                     zoomToBounds=False,  # when true, zooms to bounds when data changes
                     cluster=True,  # when true, data are clustered
                     # when true, zooms to bounds of feature (e.g. cluster) on click
                     zoomToBoundsOnClick=True,
                     # how to draw points
                     superClusterOptions=dict(
                         radius=110),  # adjust cluster size
                     )

# -----------------------------------------------
# App Layout

app.layout = html.Div([


    html.Div([
        html.Pre(children="Brassica Distribution",
                 style={"text-align": "center", "font-size": "200%", "color": "black"})
    ]),



    html.Div([
        dcc.Checklist(
             # used to identify component in callback
             id='select_species_checklist',
             options=sorted(species_options, key=lambda x: x['label']
                            ),
             value=default_species,    # values chosen by default

             # className='my_box_container',           # class of the container (div)
             # style of the container (div)
             style={'display': 'table_cell'},

             # inputClassName='my_box_input',          # class of the <input> checkbox element
                # style of the <input> checkbox element
                inputStyle={'cursor': 'pointer'},

                # labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
                labelStyle={'background': '#A5D6A7',   # style of the <label> that wraps the checkbox input and the option's label
                            'padding': '.35.0rem 0.35rem 0.35rem',
                            'border-radius': '0.4rem'},

             ),
    ]),


    html.Div([
        dcc.Checklist(
             # used to identify component in callback
             id='select_info_checklist',
             #  options=sorted(info_options, key=lambda x: x['label']
             #                 ),
             options=[
                {'label': 'GPS', 'value': 1},
                {'label': 'Detailed Description', 'value': 2},
                {'label': 'Town or Locality', 'value': 3},
                {'label': 'Region', 'value': 4},
                {'label': 'Country', 'value': 5},
                {'label': 'Former Countries', 'value': 7}
             ],
             value=default_info,    # values chosen by default

             # className='my_box_container',           # class of the container (div)
             # style of the container (div)
             style={'display': 'flex'},

             # inputClassName='my_box_input',          # class of the <input> checkbox element
             # style of the <input> checkbox element
             inputStyle={'cursor': 'pointer'},

             # labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
             labelStyle={'background': '#4495db',   # style of the <label> that wraps the checkbox input and the option's label
                         'padding': '0.5rem 1rem',
                         'border-radius': '0.5rem'},

             ),
        dcc.Checklist(
            # used to identify component in callback
            id='select_source_checklist',
            options=sorted(source_options, key=lambda x: x['label']
                           ),
            value=default_source,    # values chosen by default

            # className='my_box_container',           # class of the container (div)
            # style of the container (div)
            style={'display': 'flex'},

            # inputClassName='my_box_input',          # class of the <input> checkbox element
            # style of the <input> checkbox element
            inputStyle={'cursor': 'pointer'},

            # labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
            labelStyle={'background': '#e83d31',   # style of the <label> that wraps the checkbox input and the option's label
                        'padding': '0.5rem 1rem',
                        'border-radius': '0.5rem'},

        ),
        dcc.Checklist(
            # used to identify component in callback
            id='select_sampstat_checklist',
            options=[
                {'label': 'Wild', 'value': 100},
                {'label': 'Natural', 'value': 110},
                {'label': 'Semi-natural (wild)', 'value': 120},
                {'label': 'Semi-natural (sown)', 'value': 130},
                {'label': 'Weedy', 'value': 200},
                {'label': 'Traditional Cultivar/Landrace', 'value': 300}
            ],

            value=default_sampstat,    # values chosen by default


            # className='my_box_container',           # class of the container (div)
            # style of the container (div)
            style={'display': 'flex'},

            # inputClassName='my_box_input',          # class of the <input> checkbox element
            # style of the <input> checkbox element
            inputStyle={'cursor': 'pointer'},

            # labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
            labelStyle={'background': '#e8e831',   # style of the <label> that wraps the checkbox input and the option's label
                        'padding': '0.5rem 1rem',
                        'border-radius': '0.5rem'},

        ),
    ]),



    html.Div([
        dl.Map([dl.TileLayer(), geojson])
    ], style={'width': '100%', 'height': '72vh', 'margin': "auto", "display": "block", "position": "absolute"})
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@ app.callback(
    Output(component_id='geojson', component_property='data'),
    [Input(component_id='select_source_checklist', component_property='value'),
     Input(component_id='select_species_checklist', component_property='value'),
     Input(component_id='select_info_checklist', component_property='value'),
     Input(component_id='select_sampstat_checklist', component_property='value')
     ]
)
def update_data(source_selected, species_selected, info_selected, sampstat_selected):
    data = get_data(source_selected,
                    species_selected,
                    info_selected,
                    sampstat_selected)

    return(data)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
