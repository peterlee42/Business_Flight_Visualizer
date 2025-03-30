"""Visualizer for our graph"""
import plotly.graph_objects as go

import main
import dash
from dash import dcc, html, Output, Input, State

import plotly.io as plo

plo.renderers.default = 'browser'


def visualize_graph(graph: main.AirportsGraph, max_vertices: int = 5000):
    """Visualize graph on map"""
    graph_nx = graph.to_networkx(max_vertices)

    latitudes = []
    longitudes = []
    node_names = []

    for node in graph_nx.nodes:
        lat = graph_nx.nodes[node]['latitude']
        lon = graph_nx.nodes[node]['longitude']
        latitudes.append(lat)
        longitudes.append(lon)
        node_names.append(node)

    # edge_lons = []
    # edge_lats = []
    edge_traces = []
    for edge in graph_nx.edges:
        node1, node2 = edge
        lat1, lon1 = graph_nx.nodes[node1]['latitude'], graph_nx.nodes[node1]['longitude']
        lat2, lon2 = graph_nx.nodes[node2]['latitude'], graph_nx.nodes[node2]['longitude']
        # None separates the line segments
        # edge_lats.extend([lat1, lat2, None])
        # edge_lons.extend([lon1, lon2, None])

        edge_trace = go.Scattermap(
            mode="lines",
            lon=[lon1, lon2, None],
            lat=[lat1, lat2, None],
            line=dict(width=2, color='rgba(0, 0, 0, 0.1)'),
            hoverinfo='none'  # potentially distance value or cost of living info
            # name='Airport Connections',
            # opacity=0.2
        )
        edge_traces.append(edge_trace)

    # edge_traces = go.Scattermap(
    #     mode="lines",
    #     lon=edge_lons,
    #     lat=edge_lats,
    #     line=dict(width=2, color='rgba(0, 0, 0, 0.1)'),
    #     name='Airport Connections',
    #     #opacity=0.2
    # )

    node_trace = go.Scattermap(
        mode="markers",
        lon=longitudes,
        lat=latitudes,
        text=node_names,
        name='Airports',
        marker={'size': 6, 'color': 'black'},
    )
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        showlegend=False,
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

    # Dash App
    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H3("Airports Network Visualization"),
        dcc.Graph(id='world-graph',
                  figure=fig,
                  style={'height': '600px', 'width': '100%'}),
        html.Div(id='output', style={
                 'marginTop': '20px', 'marginLeft': '300px', 'fontSize': '18px', 'color': 'green'})
    ])

    clicked_nodes = []

    @app.callback(
        Output('output', 'children'),
        Output('world-graph', 'figure'),
        Input('world-graph', 'clickData'),
        prevent_initial_call=True
    )

    def display_click(clickData):
        """..."""
        # TODO: ADD DOCSTRING
        if not clickData or 'points' not in clickData:
            return ""

        point = clickData['points'][0]
        node_name = point['text']

        if node_name not in graph_nx.nodes:
            return ""

        # Add clicked node to list
        clicked_nodes.append(node_name)

        if len(clicked_nodes) < 2:
            change_edge_color(node_name)
            return f"Selected node: {node_name}. Click one more node.", fig

        # Compute distance
        n1, n2 = clicked_nodes[:2]
        # lat1, lon1 = graph_nx.nodes[n1]['latitude'], graph_nx.nodes[n1]['longitude']
        # lat2, lon2 = graph_nx.nodes[n2]['latitude'], graph_nx.nodes[n2]['longitude']
        # pos1 = (lat1, lon1)
        # pos2 = (lat2, lon2)
        connected = False
        for edge in graph_nx.edges(data=True):
            if n1 in edge and n2 in edge:
                print(edge[2]["weight"])
                distance_km = edge[2]["weight"]
                connected = True
        if connected:
            # Reset after two clicks
            clicked_nodes.clear()
            change_color_back()

            return f"Distance between {n1} and {n2}: {distance_km:.2f} km", fig
        else:
            clicked_nodes.clear()
            change_color_back()
            return "Selected node is not connected", fig

    app.run(debug=True)
