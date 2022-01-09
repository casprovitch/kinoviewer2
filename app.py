# -*- coding: utf-8 -*-
import json
import io
import base64
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from tree_graph import Tree_plotter
from layout import app_layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

### DATAFRAME OF DATA ###

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

#INITIALISING GRAPH PLOTTERS
tree_graph = Tree_plotter()

#################### APPLICATION LAYOUT ####################

app.layout = app_layout

#Drawing time-series 3D graph
def draw_3d_graph(contents):
    contents_string=contents[0].split(',')[1]
    decoded = base64.b64decode(contents_string)
    try:
        df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep='\t')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file. {}'.format(e),
            '{}'.format(decoded)
        ])
    df_tidy = pd.melt(df, ["id"], var_name="data_point", value_name="value")
    #fig=px.scatter_3d(df_tidy, x="id", y="data_point", z="value")
    fig=px.line_3d(df_tidy, x="id", y="data_point", z="value", line_group="id")
    fig.update_layout(clickmode='event+select')
    #return html.Div(children=[
    #    dcc.Graph(
    #        id='main-graph',
    #        figure=fig
    #        )])
    return html.Div([
            "Not yet ready, work in progress"
        ])

#Drawing kinase tree
def draw_tree(contents, graph_type):
    full_dataframe = pd.read_csv("data/{}_dataframe.tsv".format(graph_type), sep='\t')
    contents_string=contents[0].split(',')[1]
    decoded = base64.b64decode(contents_string)
    try:
        df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep='\t')
        df["id"]=[id.split(";")[0] for id in df[df.columns[0]]]
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file. {}'.format(e),
            '{}'.format(decoded)
        ])
    #Create a Tree Plotter class
    tree_graph.source_df=full_dataframe
    tree_graph.df=df
    #Draw the plot
    tree_graph.draw_plot(graph_type)
    #Access the plot from the plotter
    fig = tree_graph.fig
    return dcc.Graph(
            id='main-graph',
            figure=fig,
            config={
                #'editable': True,
                "modeBarButtonsToAdd": [
                    "drawline",
                    "drawopenpath",
                    "drawclosedpath",
                    "drawcircle",
                    "drawrect",
                    "eraseshape",
                    "hoverCompareCartesian",
    ]
                    },
            style={
               'width': '100%',
               'height': '100%'})

#Update name of uploaded file
@app.callback(
    Output('filename-text', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'))
def update_file_name(contents, filename):
    if contents is not None:
        children=filename
    else:
        children='Upload a data file to begin'
    return children

#Help window
@app.callback(
    Output("help-popup", "is_open"),
    [Input("help-button", "n_clicks"), Input("close-help", "n_clicks")],
    [State("help-popup", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#Draw graph on button click
@app.callback(
    Output('output-data-upload', 'children'),
    State("graph-type","value"),
    Input("generate-button","n_clicks"),
    Input('upload-data', 'contents'))
def generate_graph(value, n_clicks, contents):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'generate-button' in changed_id:
        children=draw_tree(contents, value)
        return [children, None]

#On-click data
@app.callback(
    Output('click-data', 'children'),
    Input('main-graph', 'clickData'),
    State("graph-type","value"))
def display_click_data(clickData, graph_type):
    if graph_type=="kinasetree":
        id = clickData['points'][0]['customdata'][0]
    if graph_type=="phosphatasetree":
        id = clickData['points'][0]['x']
    uniprot_id = full_dataframe[full_dataframe['id.coral']==id]['id.uniprot'].values[0]
    markdown_string='''
        ID: **{id}**
        Uniprot ID: {uniprot_id}
        '''.format(id=id, uniprot_id=uniprot_id)
    return html.Div(id='onclick-data',children=[
        dcc.Markdown(id='onclick-text',children=markdown_string),
        html.A("Uniprot Data", href='https://www.uniprot.org/uniprot/{uniprot_id}'.format(uniprot_id=uniprot_id), target="_blank"),
        html.P(json.dumps(clickData, indent=2)),
        html.Div([
        html.Button("Download Data", id="download-button"),
        dcc.Download(id="download-data")])
                            ], style={'vertical-align': 'top'}
                    )

##Updating graph display
@app.callback(
    Output('main-graph', 'figure'),
    Input('show-paths', 'value'),
    Input('show-labels', 'value'),
    Input('display-style', 'value'),
    prevent_initial_call=True)
def update_paths(show_paths, show_labels, display_style):
    tree_graph.show_paths=show_paths
    tree_graph.show_labels=show_labels
    tree_graph.display_style=display_style
    tree_graph.update_plot()
    return tree_graph.fig

#Data Download
@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    State('onclick-data', 'children'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def func(n_clicks, children):
    return dict(content=json.dumps(children),filename='output.txt')

if __name__ == '__main__':
    app.run_server(debug=True)
#    app.run_server(debug=False)
