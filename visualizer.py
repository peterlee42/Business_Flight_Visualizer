"""Visualizer for our graph"""

from typing import Any

import plotly.graph_objects as go

import plotly.io as plo
import dash
from dash import dcc, html, Output, Input, State, ctx

import main

plo.renderers.default = "browser"


def visualize_graph_app(graph: main.AirportsGraph, max_vertices: int = 100) -> None:
    """Interactive Graph Visualizer"""
    graph_nx = graph.to_networkx(max_vertices)

    node_traces = []
    for node in graph_nx.nodes:
        lat1 = graph_nx.nodes[node]["latitude"]
        lon1 = graph_nx.nodes[node]["longitude"]
        id1 = graph_nx.nodes[node]["id"]
        country1 = graph_nx.nodes[node]['country']

        node_trace = go.Scattermap(
            mode="markers",
            lon=[lon1],
            lat=[lat1],
            text=[node],
            name=country1,
            marker={"size": 4, "color": "black"},
            ids=[id1],
        )
        node_traces.append(node_trace)

    edge_traces = []
    text_traces = []
    for edge in graph_nx.edges(data=True):
        node1 = edge[0]
        node2 = edge[1]
        lat1, lon1 = (
            graph_nx.nodes[node1]["latitude"],
            graph_nx.nodes[node1]["longitude"],
        )
        lat2, lon2 = (
            graph_nx.nodes[node2]["latitude"],
            graph_nx.nodes[node2]["longitude"],
        )

        edge_trace = go.Scattermap(
            mode="lines+text",
            lon=[lon1, lon2, None],
            lat=[lat1, lat2, None],
            line={"width": 2, "color": "rgba(0, 0, 0, 0.1)"},
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
            text=[str(edge[2]["weight"]) + "km"],
            textposition="middle center",
            hoverinfo="none",
            showlegend=False,
            textfont={"size": 8},
        )
        text_traces.append(text_trace)

    fig = go.Figure(data=edge_traces + node_traces + text_traces)
    fig.update_layout(
        margin={"l": 0, "t": 0, "b": 0, "r": 0},
        showlegend=False,
        uirevision="constant",
        map={
            "center": {"lon": 10, "lat": 10},
            "style": "open-street-map",
            "zoom": 1,
        },
        title="Airports Network Visualization",
    )

    node_data_map = {}
    for i, data in enumerate(fig.data):
        if data not in edge_traces and data not in text_traces and data.text:
            node_data_map[data.text[0]] = i

    def change_node_marker(node_name: str, marker_data: dict[str, Any]) -> go.Figure:
        """Highlight the chosen vertex"""
        index = node_data_map.get(node_name)
        if index is not None:
            fig.data[index].marker = marker_data
            return fig
        return fig

    # Dash App
    app = dash.Dash(__name__)

    app.layout = html.Div(
        style={
            "backgroundColor": "#e0e1dd",
            "fontFamily": "Arial, sans-serif",
            "padding": "20px",
        },
        children=[
            html.Div(
                [
                    html.H2(
                        "Business Travel Flight Visualizer",
                        style={"textAlign": "center", "color": "#0d1b2a"},
                    ),
                    dcc.Graph(
                        id="world-graph",
                        figure=fig,
                        style={
                            "height": "60vh",
                            "width": "100%",
                            "border": "2px solid",
                            "borderRadius": "5px",
                            "max-width": "1000px",
                        },
                    ),
                    html.H3(
                        "Search for Nearby Adjacent Airports",
                        style={
                            "textAlign": "center",
                            "color": "#0d1b2a",
                        },
                    ),
                    html.Div(
                        [
                            html.Label("Max Distance: ", style={"marginRight": "10px"}),
                            dcc.Input(
                                id="my-input",
                                value="1000",
                                type="text",
                                style={
                                    "width": "150px",
                                    "padding": "5px",
                                    "border": "1px solid #ccc",
                                    "borderRadius": "3px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                        },
                    ),
                    html.Button(
                        id="submit-button-state",
                        children="Submit",
                        style={
                            "display": "block",
                            "margin": "10px auto",
                            "padding": "10px 20px",
                            "backgroundColor": "#007BFF",
                            "color": "#fff",
                            "border": "none",
                            "borderRadius": "5px",
                            "cursor": "pointer",
                        },
                    ),
                    html.Div(
                        id="output",
                        style={
                            "textAlign": "center",
                            "marginTop": "10px",
                            "fontSize": "16px",
                            "color": "green",
                        },
                    ),
                    html.Div(
                        [
                            html.Label("Search airport: ", style={"marginRight": "10px"}),
                            dcc.Input(
                                id="search-input",
                                value="",
                                placeholder="Enter airport name",
                                type="text",
                                style={
                                    "width": "150px",
                                    "padding": "5px",
                                    "border": "1px solid #ccc",
                                    "borderRadius": "3px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "margin": "20px 0",
                        },
                    ),
                    html.Div(
                        id="search-output",
                        style={
                            "textAlign": "center",
                            "marginTop": "10px",
                            "fontSize": "16px",
                            "color": "green",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flex-direction": "column",
                    "align-items": "center",
                },
            )
        ],
    )

    # Map the node id to their names
    clicked_nodes = {}

    # Function output
    # This list will be edited in the function ONLY where it is supposed to be edited
    # It is used to store the outputs of previous callbacks of the function and update the webpage
    # without losing previous data
    output = ["", "", fig]

    @app.callback(
        Output("output", "children"),
        Output("search-output", "children"),
        Output("world-graph", "figure"),
        Input("world-graph", "clickData"),
        Input("my-input", "value"),
        Input("search-input", "n_submit"),
        State("search-input", "value"),
        Input("submit-button-state", "n_clicks"),
        prevent_initial_call=True,
    )
    def display_click(clickdata: Any, max_distance: Any, _unused_n_submit: Any, search_input: Any,
                      _unused_button_state: Any) -> tuple[str, str, go.Figure]:
        """Display the change(s) on the webpage based on any input"""
        if ctx.triggered_id == 'submit-button-state':
            if len(clicked_nodes) == 0:
                output[0] = "Please select an airport"
                return output[0], output[1], output[2]

            id_list = list(clicked_nodes.keys())

            close_airport_ids = main.AirportsGraph.get_close_airports_adjacent(
                graph, id_list, int(max_distance)
            )
            rank_airport_ids = main.AirportsGraph.rank_airports(graph, close_airport_ids, 5)
            rank_airport_names = graph.get_airport_names_from_id(rank_airport_ids)

            res = ", ".join(rank_airport_names)
            # Reset clicked nodes
            for node_id in clicked_nodes:
                change_node_marker(clicked_nodes[node_id], {"color": "black", "size": 4})
            clicked_nodes.clear()
            # Highlight the output nodes
            for name in rank_airport_names:
                if name not in clicked_nodes.values():
                    clicked_nodes[graph.get_airport_id_from_names([name])[0]] = name
                    change_node_marker(name, {"color": "green", "size": 10})

            output[0] = f"Closest airports: {res}"
            return output[0], output[1], output[2]

        elif ctx.triggered_id == "world-graph":
            if not clickdata or "points" not in clickdata:
                return output[0], output[1], output[2]

            point = clickdata["points"][0]
            node_name = point["text"]
            if not point.get("id"):
                return (output[0], output[1], output[2])
            node_id = point["id"]

            if node_name not in graph_nx.nodes:
                return output[0], output[1], output[2]

            if node_id in clicked_nodes:
                # Unselect the node
                del clicked_nodes[node_id]
                change_node_marker(node_name, {"color": "black", "size": 4})
            else:
                # Add clicked node to list
                clicked_nodes[node_id] = node_name
                change_node_marker(node_name, {"color": "blue", "size": 10})

            result = ", ".join(clicked_nodes.values())

            output[0] = f"Selected node(s): {result}"
            return output[0], output[1], output[2]

        elif ctx.triggered_id == "my-input":
            result = ", ".join(clicked_nodes.values())

            output[0] = f"Selected node(s): {result}"
            return output[0], output[1], output[2]

        elif ctx.triggered_id == "search-input":
            if search_input:
                possibles = set()
                for curr_node in graph_nx.nodes:
                    if search_input.lower() in curr_node.lower():
                        possibles.add(curr_node)
                if len(possibles) == 0:
                    output[1] = "No airports found"
                    return output[0], output[1], output[2]
                else:
                    result = ", ".join(possibles)
                    output[1] = f"Possible airports: {result}"
                    return output[0], output[1], output[2]

        return output[0], output[1], output[2]

    app.run()


def visualize_graph(graph: main.AirportsGraph, max_vertices: int = 7000):
    """Visualize airports and connections on a map"""
    graph_nx = graph.to_networkx(max_vertices)

    latitudes = []
    longitudes = []
    node_names = []
    degrees = []
    degree_size = []

    for node in graph_nx.nodes:
        lat = graph_nx.nodes[node]["latitude"]
        lon = graph_nx.nodes[node]["longitude"]
        global_piece_index = graph_nx.nodes[node]["global_piece_index"]
        country = graph_nx.nodes[node]["country"]

        latitudes.append(lat)
        longitudes.append(lon)
        node_names.append(f"Name: {node} | Country: {country} | Global Piece Index: {global_piece_index}")

        vertex_degree = graph_nx.degree(node)

        degrees.append(vertex_degree)

        # Our scaling factor which is bounded above by size 20. Max size is 20, min size is 5.
        degree_size.append(20 - (150 / (vertex_degree + 10)))

    edge_lons = []
    edge_lats = []
    for edge in graph_nx.edges(data=True):
        node1, node2 = edge[0], edge[1]
        lat1, lon1 = (
            graph_nx.nodes[node1]["latitude"],
            graph_nx.nodes[node1]["longitude"],
        )
        lat2, lon2 = (
            graph_nx.nodes[node2]["latitude"],
            graph_nx.nodes[node2]["longitude"],
        )
        # None separates the line segments
        edge_lats.extend([lat1, lat2, None])
        edge_lons.extend([lon1, lon2, None])

    fig = go.Figure(
        go.Scattermap(
            mode="lines",
            lon=edge_lons,
            lat=edge_lats,
            line={"color": "#76c893", "width": 2},
            name="Airport Connections",
            opacity=0.2,
        )
    )

    colour_scale = [[0, "blue"], [1, "red"]]

    fig.add_trace(
        go.Scattermap(
            mode="markers",
            lon=longitudes,
            lat=latitudes,
            text=node_names,
            name="Airports",
            marker={"size": degree_size,
                    "color": degrees,
                    "colorscale": colour_scale,
                    "colorbar": {
                        "title": "Number of Neighbours",
                        "xanchor": "left",
                        "yanchor": "middle",
                        "len": 0.5,
                        "thickness": 10,
                    }
                    }
        )
    )

    fig.update_layout(
        margin={"l": 0, "t": 30, "b": 0, "r": 0},
        map={
            "center": {"lon": 10, "lat": 10},
            "style": "open-street-map",
            "zoom": 1,
        },
        title="Airports Network Visualization",
    )
    fig.show()
