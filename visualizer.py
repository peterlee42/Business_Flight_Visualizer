"""Visualizer for our graph"""
import plotly.graph_objects as go
import plotly.io as plo
import dash
from dash import dcc, html, Output, Input, ctx
import main

import plotly.io as plo

plo.renderers.default = 'browser'


def visualize_graph(graph: main.AirportsGraph, max_vertices: int = 5000, output_file: str = ''):
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

    edge_lons = []
    edge_lats = []
    for edge in graph_nx.edges:
        node1, node2 = edge
        lat1, lon1 = graph_nx.nodes[node1]['latitude'], graph_nx.nodes[node1]['longitude']
        lat2, lon2 = graph_nx.nodes[node2]['latitude'], graph_nx.nodes[node2]['longitude']
        # None separates the line segments
        edge_lats.extend([lat1, lat2, None])
        edge_lons.extend([lon1, lon2, None])

    fig = go.Figure(go.Scattermap(
        mode="lines",
        lon=edge_lons,
        lat=edge_lats,
        line={'color': '#11cd2f', 'width': 2},
        name='Airport Connections',
        opacity=0.2
    ))

    fig.add_trace(go.Scattermap(
        mode="markers",
        lon=longitudes,
        lat=latitudes,
        text=node_names,
        name='Airports',
        marker={'size': 6, 'color': 'blue'},
        opacity=0.6
    ))

    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        showlegend=False,
        map={
            'center': {'lon': 10, 'lat': 10},
            'style': "open-street-map",
            'zoom': 1,
        },
        title="Airports Network Visualization"
    )

    if output_file:
        fig.write_image(output_file)
    else:
        fig.show()
