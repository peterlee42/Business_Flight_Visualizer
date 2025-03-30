"""Visualizer for our graph"""
import plotly.graph_objects as go
from typing import Any, Optional

import plotly.io as plo
import dash
from dash import dcc, html, Output, Input, ctx
import main

plo.renderers.default = 'browser'


def visualize_graph(graph: main.AirportsGraph, max_vertices: int = 7000) -> None:
    """Visualize graph on map"""
    graph_nx = graph.to_networkx(max_vertices)

    node_traces = []
    for node in graph_nx.nodes:
        lat1 = graph_nx.nodes[node]['latitude']
        lon1 = graph_nx.nodes[node]['longitude']
        id1 = graph_nx.nodes[node]['id']

        node_trace = go.Scattermap(
            mode="markers",
            lon=[lon1],
            lat=[lat1],
            text=[node],
            name="Airports",
            marker={'size': 4, 'color': 'black'},
            ids=[id1]
        )
        node_traces.append(node_trace)

    edge_traces = []
    text_traces = []
    for edge in graph_nx.edges(data=True):
        node1 = edge[0]
        node2 = edge[1]
        lat1, lon1 = graph_nx.nodes[node1]['latitude'], graph_nx.nodes[node1]['longitude']
        lat2, lon2 = graph_nx.nodes[node2]['latitude'], graph_nx.nodes[node2]['longitude']

        edge_trace = go.Scattermap(
            mode="lines+text",
            lon=[lon1, lon2, None],
            lat=[lat1, lat2, None],
            line={"width": 2, "color": 'rgba(0, 0, 0, 0.1)'},
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
            textfont={"size": 8}
        )
        text_traces.append(text_trace)

    fig = go.Figure(data=edge_traces + node_traces + text_traces)
    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        showlegend=False,
        map={
            'center': {'lon': 10, 'lat': 10},
            'style': "open-street-map",
            'zoom': 1,
        },
        title="Airports Network Visualization",
    )

    def change_node_color(node_name: str) -> go.Figure:
        """highlight the vertex chosen"""
        for i, value in enumerate(fig.data):
            if value in edge_traces or value in text_traces:
                pass
            else:
                if node_name == fig.data[i].text[0]:
                    fig.data[i].marker = {'size': 10, 'color': 'black'}
                    return fig
        return fig

    def change_node_back() -> go.Figure:
        """change all the vertex back to original state"""
        for i, value in enumerate(fig.data):
            if value in edge_traces or value in text_traces:
                pass
            else:
                fig.data[i].marker = {'size': 4, 'color': 'black'}
        return fig

    # Dash App
    app = dash.Dash(__name__)

    app.layout = html.Div(
        style={
            'backgroundColor': '#e0e1dd',
            'fontFamily': 'Arial, sans-serif',
            'padding': '20px'
        },
        children=[html.Div([
            html.H2(
                "Business Travel Flight Visualizer",
                style={'textAlign': 'center', 'color': '#0d1b2a'}
            ),
            dcc.Graph(
                id='world-graph',
                figure=fig,
                style={
                    'height': '60vh',
                    'width': '100%',
                    'border': '2px solid',
                    'borderRadius': '5px',
                    'max-width': '1000px'
                }
            ),
            html.Div(
                [
                    html.Label("Max Distance: ", style={
                               'marginRight': '10px'}),
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
        ],
            style={
                'display': 'flex',
                'flex-direction': 'column',
                'align-items': 'center'
            }
        )]
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
    def display_click(clickdata: Any, max_distance: Any, button_state: Any) -> tuple[str, go.Figure]:
        """perform computation from the input and display on the webpage"""
        if ctx.triggered_id == 'submit-button-state':
            if len(clicked_node) == 0:
                return 'please click one airport', fig

            id_list = []
            for i in clicked_node:
                id_list.append(i['points'][0]['id'])

            close_airport_ids = main.AirportsGraph.get_close_airports(
                    graph, id_list, int(max_distance))
            close_airport_names = [graph._vertices[airport].item.name for airport in close_airport_ids]
            res = ', '.join(close_airport_names)
            change_node_back()
            clicked_nodes_name.clear()
            clicked_node.clear()
            return f'The intersection airports include: {res}', fig

        elif ctx.triggered_id == 'world-graph':
            if not clickdata or 'points' not in clickdata:
                return "", fig

            point = clickdata['points'][0]
            node_name = point['text']

            if node_name not in graph_nx.nodes:
                return "", fig

            # Add clicked node to list
            clicked_nodes_name.append(node_name)
            clicked_node.append(clickdata)
            change_node_color(node_name)
            result = ', '.join(clicked_nodes_name)

            return f'Selected node: {result}', fig

        elif ctx.triggered_id == 'my-input':
            result = ', '.join(clicked_nodes_name)
            return f'Selected node: {result}', fig

        return "", fig

    app.run(debug=True)
