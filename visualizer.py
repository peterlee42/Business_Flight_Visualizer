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

import plotly.io as plo

plo.renderers.default = 'browser'


def visualize_graph(graph: main.AirportsGraph, max_vertices: int = 5000, output_file: str = ''):
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
        map={
            'center': {'lon': 10, 'lat': 10},
            'style': "open-street-map",
            'center': {'lon': -20, 'lat': -20},
            'zoom': 1,
        },
        title="Airports Network Visualization"
    )

    if output_file:
        fig.write_image(output_file)
    else:
        fig.show()
