# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#################### APPLICATION LAYOUT ####################

app_layout = html.Div(children=[
    html.H1(
        children='KINOVIEWER 2',
        style={
            'textAlign': 'center',
            'color': 'black'
        }
    ),
    html.Div(children=[

            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '300px',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px',
                        'display': 'inline-block',
                        'vertical-align': 'top'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                html.Div(
                    id="filename-text",
                    children="Upload a data file to begin",
                    style={'display': 'inline-block','vertical-align': 'top', 'margin': '10px'}),
                dcc.Checklist(
                    id="use-default-dataset",
                    options=[
                            {'label': 'Use default dataset', 'value': 'default'},
                        ],
                        value=[]
                    )
            ],style={'display': 'inline-block','vertical-align': 'top', 'margin': '10px'}),
            html.Div([
                html.Div(children=[
                    html.Div(children=[
                        html.A('Choose a graph type'),
                        dcc.RadioItems(
                            id="graph-type",
                            options=[
                                {'label': 'Kinase Tree', 'value': 'kinase'},
                                {'label': 'Exampletase Tree (test)', 'value': 'exampletase'}
                            ],
                            value='kinase',
                            labelStyle={'display': 'block'},
                            #style={'display': 'inline-block', 'margin': '10px'}
                        ),
                        ],style={'display': 'inline-block', 'margin': '10px'}),
                    html.Button("Generate Graph", id="generate-button",
                                style={'textAlign': 'center',
                                   'width': '200px',
                                   'height': '60px',
                                   'vertical-align': 'top',
                                   'display': 'inline-block',
                                   'background-color': 'green',
                                   'color': 'white'})
                        ], style={'display': 'inline-block'}),
                ],style={'display': 'inline-block','vertical-align': 'top', 'margin': '10px'}),
            html.Button("Help?", id="help-button",
                        style={'textAlign': 'center',
                               'width': '200px',
                               'height': '60px',
                               'margin': '10px',
                               'vertical-align': 'top',
                               'display': 'inline-block',
                               'background-color': 'blue',
                               'color': 'white',
                               'float': 'right'}),

            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("How to use"), close_button=True),
                    dbc.ModalBody(children=[
                                        html.Div("""Upload a CSV file using button in top left corner"""),
                                        html.Div("""CSV file needs to contain 2 columns:\n- protein ID (Uniprot)\n- oberved values (abundance or log)\nseparated by either tab or comma"""),
                                        html.Div("""\nSelect Graph Type and Options using radio buttons"""),
                                        html.Div("""\nClick Generate Graph to draw it"""),
                                        html.Div(),
                                            ],style={'white-space': 'pre'}),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close-help", className="ms-auto", n_clicks=0
                        )
                    )
                ],
                id="help-popup",
                size="lg",
                backdrop=False,
                is_open=False)
    
                ]),

    html.Div([
        html.Div(id='output-data-upload',
                     style={'width': '70%', 'height': '100%',
                            'border': 'thin lightgrey solid',
                            'display': 'inline-block'}),
        html.Div(id='sidebar',
                  children=
            [
                html.Div(
                    id='options-menu',
                    children=[
                html.H3('Options'),
                    html.H4('Choose display style'),
                    dcc.RadioItems(
                        id="display-style",
                        options=[
                            {'label': 'Gradient colour by values', 'value': 'gradient-colour'},
                            {'label': 'Colour by group/Size by values', 'value': 'group-colour'},
                        ],
                        value='gradient-colour',
                        labelStyle={'display': 'block'},
                        #style={'display': 'inline-block'}
                    ),
                    html.H4('Choose visiblity of labels'),
                    dcc.RadioItems(
                        id="show-labels",
                        options=[
                            {'label': 'All labels', 'value': 'all'},
                            {'label': 'Results labels', 'value': 'results'},
                            {'label': 'No labels', 'value': 'none'}
                        ],
                        value='all',
                        labelStyle={'display': 'block'},
                        #style={'display': 'inline-block'}
                    ),
                    html.H4('Choose visibility of paths'),
                    dcc.RadioItems(
                        id="show-paths",
                        options=[
                            {'label': 'All paths', 'value': 'all'},
                            {'label': 'Results paths', 'value': 'results'},
                            {'label': 'No paths', 'value': 'none'}
                        ],
                        value='all',
                        labelStyle={'display': 'block'},
                        #style={'display': 'inline-block'}
                    )],
                    style={
                        'float': 'right',
                        #'border': 'thin lightgrey solid'
                        }),

                    html.Div(children=[
                        dcc.Markdown("""
                                **Click Data**

                                Click on points in the graph to display additional data below
                            """,style={'text-align': 'centre'}),
                        html.Pre(id='click-data', style={'vertical-align': 'right', 'width': '30vh', 'height': '30vh'}),
                        ], style={'vertical-align': 'top', 'width': '30vh', 'height': '30vh'})
                ], style={'vertical-align': 'top', 'display': 'inline-block'})

        ], style={'height': '90%', 'width': '90%','margin': '10px','vertical-align': 'top','border': 'thin lightgrey solid'}),
    ], style={'height': '100vh', 'width': '100vw'})

if __name__ == '__main__':
    app.layout = app_layout
    app.run_server(debug=True)