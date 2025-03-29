"""CSC111 Winter 2025 Exercise 3-4 (Graphs Visualization)

Module Description
==================

This module contains some Python functions that you can use to visualize the graphs
you're working with on this assignment. You should not modify anything in this file.
It will not be submitted for grading.

Disclaimer: we didn't have time to make this file fully PythonTA-compliant!

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 Mario Badr, David Liu, and Isaac Waller.
"""
import plotly.graph_objects as go

import main
import dash
from dash import dcc, html, Output, Input, State, ctx
from geopy.distance import great_circle

import plotly.io as plo

plo.renderers.default = 'browser'


def visualize_graph(graph: main.AirportsGraph, max_vertices: int = 5000, output_file: str = ''):
    """Visualize graph on map"""
    graph_nx = graph.to_networkx(max_vertices)

    # latitudes = []
    # longitudes = []
    # node_names = []

    node_traces = []
    for node in graph_nx.nodes:
        lat1 = graph_nx.nodes[node]['latitude']
        lon1 = graph_nx.nodes[node]['longitude']
        id1 = graph_nx.nodes[node]['id']
        # latitudes.append(lat1)
        # longitudes.append(lon1)
        # node_names.append(node)
        node_trace = go.Scattermap(
            mode="markers",
            lon = [lon1],
            lat = [lat1],
            text = [node],
            name = "Airports",
            marker={'size': 4, 'color': 'black'},
            ids = [id1]
        )
        node_traces.append(node_trace)

    edge_traces = []
    text_traces = []
    for edge in graph_nx.edges(data=True):
        node1= edge[0]
        node2= edge[1]
        lat1, lon1 = graph_nx.nodes[node1]['latitude'], graph_nx.nodes[node1]['longitude']
        lat2, lon2 = graph_nx.nodes[node2]['latitude'], graph_nx.nodes[node2]['longitude']

        edge_trace = go.Scattermap(
            mode="lines+text",
            lon=[lon1, lon2, None],
            lat=[lat1, lat2, None],
            line=dict(width=2, color='rgba(0, 0, 0, 0.1)'),
        )
        edge_traces.append(edge_trace)

        # Compute the midpoint coordinates for the label
        mid_lon = (lon1 + lon2) / 2
        mid_lat = (lat1 + lat2) / 2

        # Create a separate trace to display the distance label at the midpoint
        text_trace = go.Scattermap(
            mode="text",
            lon=[mid_lon],
            lat=[mid_lat],
            text=[str(edge[2]['weight']) + 'km'],
            textposition="middle center",
            showlegend=False,
            textfont=dict(size=8)
        )
        text_traces.append(text_trace)

    fig = go.Figure(data = edge_traces + node_traces + text_traces)
    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        showlegend = False,
        map={
            'center': {'lon': 10, 'lat': 10},
            'style': "open-street-map",
            'center': {'lon': -20, 'lat': -20},
            'zoom': 1,
        },
        title="Airports Network Visualization",
    )

    def change_edge_color(node_name):
        for i, edge in enumerate(list(graph_nx.edges)):
            if node_name in edge[0] or node_name in edge[1]:
                fig.data[i].line.color = 'rgba(0, 0, 0, 0.8)'
            else:
                fig.data[i].line.color = 'rgba(0, 0, 0, 0.1)'
        return fig 

    def change_color_back():
        for i, edge in enumerate(list(graph_nx.edges)):
                fig.data[i].line.color = 'rgba(0, 0, 0, 0.1)'
        return fig 
    
    def change_node_color(node_name):
        for i, value in enumerate(fig.data):
            if value in edge_traces or value in text_traces:
                pass
            else:
                if node_name == fig.data[i].text[0]:
                    fig.data[i].marker = {'size': 10, 'color': 'black'}
                    #print(fig.data[i])
                    return fig
    
    def change_node_back():
        for i, value in enumerate(fig.data):
            if value in edge_traces or value in text_traces:
                pass
            else:
                fig.data[i].marker = {'size': 4, 'color': 'black'}
        return fig


    # Dash App
    app = dash.Dash(__name__)
    # app.layout = html.Div([
    #     html.H3("Business travel flight visualizer"),
    #     dcc.Graph(id='world-graph', 
    #               figure=fig,
    #               style={'height': '600px', 'width': '100%'}),
    #     html.Div(
    #         ["Max Distance: ", dcc.Input(id='my-input', value='1000', type='text')], 
    #         style={'marginLeft': '40%','marginTop': '2%'}),
    #     html.Div(
    #         "Output: ",
    #         style = {'marginLeft':'30%','marginTop':'0.2%'}),
    #     html.Button(id='submit-button-state', children='Submit',style={'marginLeft':'60%'}),
    #     html.Div(id='output', style={'marginTop': '0.5%', 'fontSize': '14px', 'color': 'green'})
    # ])
    app.layout = html.Div(
        style={
            'backgroundColor': '#f9f9f9',
            'fontFamily': 'Arial, sans-serif',
            'padding': '20px'
        },
        children=[
            html.H3(
                "Business Travel Flight Visualizer",
                style={'textAlign': 'center', 'color': '#333'}
            ),
            dcc.Graph(
                id='world-graph',
                figure=fig,
                style={
                    'height': '600px',
                    'width': '100%',
                    'border': '2px solid #ccc',
                    'borderRadius': '5px',
                    'boxShadow': '2px 2px 12px rgba(0,0,0,0.1)'
                }
            ),
            html.Div(
                [
                    html.Label("Max Distance: ", style={'marginRight': '10px'}),
                    dcc.Input(
                        id='my-input',
                        value='1000',
                        type='text',
                        style={
                            'width': '150px',
                            'padding': '5px',
                            'border': '1px solid #ccc',
                            'borderRadius': '3px'
                        }
                    )
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'margin': '20px 0'
                }
            ),
            html.Div(
                "Output: ",
                style={
                    'textAlign': 'center',
                    'marginBottom': '10px',
                    'color': '#333',
                    'fontWeight': 'bold'
                }
            ),
            html.Button(
                id='submit-button-state',
                children='Submit',
                style={
                    'display': 'block',
                    'margin': '0 auto',
                    'padding': '10px 20px',
                    'backgroundColor': '#007BFF',
                    'color': '#fff',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }
            ),
            html.Div(
                id='output',
                style={
                    'textAlign': 'center',
                    'marginTop': '10px',
                    'fontSize': '16px',
                    'color': 'green'
                }
            )
        ]
        )

    clicked_nodes_name = []
    clicked_node = []

    @app.callback(
        Output('output', 'children'),
        Output('world-graph', 'figure'),
        Input('world-graph', 'clickData'),
        Input('my-input', 'value'),
        Input('submit-button-state', 'n_clicks'),
        prevent_initial_call=True
    )
    def display_click(clickData, max_distance, button_state):
        # print(clickData, max_distance)
        # print(ctx.triggered_id)
        result = ""
        if ctx.triggered_id == 'submit-button-state':
            if len(clicked_node) == 0:
                return 'please lick one airport'
            
            id_list = []
            for i in clicked_node:
                id_list.append(i['points'][0]['id'])
                result1 = main.AirportsGraph.get_close_airports(graph, id_list, int(max_distance))
            res = ', '.join(result1)
            change_node_back()
            #change_color_back()
            clicked_nodes_name.clear()
            clicked_node.clear()
            return f'The intersection airports include: {res}', fig
        
        elif ctx.triggered_id == 'world-graph':
            #print(clickData)
            if not clickData or 'points' not in clickData:
                return ""
            
            point = clickData['points'][0]
            node_name = point['text']

            if node_name not in graph_nx.nodes:
                return ""
            
            # if len(clicked_node) < 2:
            #     change_edge_color(node_name)

            # Add clicked node to list
            clicked_nodes_name.append(node_name)
            clicked_node.append(clickData)
            change_node_color(node_name)
            result = ', '.join(clicked_nodes_name)

            return f'Selected node: {result}',fig
        
        elif ctx.triggered_id == 'my-input':
            return f'Selected node: {result}', fig

        # # Compute distance
        # n1, n2 = clicked_nodes[:2]
        # # lat1, lon1 = graph_nx.nodes[n1]['latitude'], graph_nx.nodes[n1]['longitude']
        # # lat2, lon2 = graph_nx.nodes[n2]['latitude'], graph_nx.nodes[n2]['longitude']
        # # pos1 = (lat1, lon1)
        # # pos2 = (lat2, lon2)

        # connected = False
        # for edge in graph_nx.edges(data = True):
        #     if n1 in edge and n2 in edge:
        #         distance_km = edge[2]["weight"]
        #         connected = True
        # if connected:
        #     # Reset after two clicks
        #     clicked_nodes.clear()
        #     change_color_back()

        #     return f"Distance between {n1} and {n2}: {distance_km:.2f} km", fig
        # else:
        #     clicked_nodes.clear()
        #     change_color_back()
        #     return "Selected node is not directly connected", fig


    app.run(debug=True)

    # if output_file:
    #     fig.write_image(output_file)
    # else:
    #     fig.show()