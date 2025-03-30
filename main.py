"""Our graph ADT"""
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt

import pandas as pd

from airports_data import load_data
import networkx as nx


@dataclass
class Location:
    """A location, showing the city, country, and timezone

    Instance Attributes:
        - city: The city of the location
        - country: The country for the location
        - timezone: The timezone for the location

    Representation Invariants:
        - self.city != ''
        - self.country != ''
        - self.timezone != ''
    """
    city: str
    country: str
    timezone: str


class _AirportVertex:
    """Airport Vertex Class

    Instance Attributes:
    - id: The OpenFlights id of an airport
    - name: The name of an airport
    - altitude: The altitude of an airport
    - coordinates: The coordinates of an airport on map using longitude and latitude
    - location: The location of an airport

    Representation Invariants:
    - self.id >= 0
    - self.name != ''
    - self.altitude > 0
    - self.coordinates != tuple()
    """
    id: int
    name: str
    altitude: int
    coordinates: tuple[float, float]
    location: Location

    def __init__(self, airport_id: int, airport_name: str, airport_altitude: int,
                 airport_coordinates: tuple[float, float], airport_location: Location):
        self.id = airport_id
        self.name = airport_name
        self.altitude = airport_altitude
        self.coordinates = airport_coordinates
        self.location = airport_location


# TODO: ADD IMPLEMENTATION FOR WEIGHTED VERTICES BASED ON SAFETY INDEX!!!
class AirportsGraph:
    """A weighted graph used to represent airport connections and the distances of the distance of each route"""

    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps airport id to _Vertex object.
    #     - _edges:
    #         A list of edges in the graph
    #     - _edge_indices:
    #         A collection of the edge indices contained in this graph.
    #         Maps vertex item (id) to edge index.

    _vertices: dict[Any, _AirportVertex]
    _edges: list[list[int]]
    _edge_indices: dict[Any, int]

    def __init__(self):
        self._vertices = {}
        self._edges = []
        self._edge_indices = {}

        # TODO: Fix implementation (maybe do one like EX4)

    def add_vertex(self, airport_id: int, item: _AirportVertex) -> None:
        """Add an airport to the graph using its id"""
        if airport_id not in self._vertices:
            self._vertices[airport_id] = item

            # add new row of zeroes to make this a nxn matrix
            for row in self._edges:
                row.append(0)
            # add another column of zeroes
            self._edges.append([0] * (len(self._edges) + 1))
            self._edge_indices[airport_id] = len(self._edge_indices) - 1

    def add_edge(self, source_id: int, destination_id: int) -> None:
        """Add an edge to the graph"""
        if source_id in self._vertices and destination_id in self._vertices:
            src_id_index = self._edge_indices[source_id]
            dest_id_index = self._edge_indices[destination_id]

            # case if edge already made from other side to improve speed. we assume 0 means edge does not exist.
            if self._edges[src_id_index][dest_id_index] != 0:
                return
            else:
                distance = self.get_distance(source_id, destination_id)

                self._edges[src_id_index][dest_id_index] = distance
                self._edges[dest_id_index][src_id_index] = distance

        else:
            raise KeyError(
                "Source ID or Destination ID do not exist in this graph.")

    def get_vertex(self, airport_id: int) -> Optional[_AirportVertex]:
        """Get a vertex from the graph"""
        return self._vertices.get(airport_id)

    def get_neighbours(self, airport_id: int) -> set:
        """Return a set of all neighbours ids of the given airport id"""

        if airport_id not in self._vertices:
            raise ValueError
        else:
            airport_index = self._edge_indices[airport_id]
            neighbours = set()

            for i, weight in enumerate(self._edges[airport_index]):
                if weight != 0:
                    for other_airport_id, other_index in self._edge_indices.items():
                        if other_index == i:
                            neighbours.add(other_airport_id)

            return neighbours

    def get_edges(self) -> list[list[int]]:
        """Get all the edges in the graph. This will return a matrix of edge weights."""
        return self._edges

    def get_distance(self, airport_id1: int, airport_id2: int) -> int:
        """Return the rounded integer distance (in kilometers) between the given two airports"""
        airport1_coords = self._vertices[airport_id1].coordinates
        airport2_coords = self._vertices[airport_id2].coordinates

        lat1 = radians(airport1_coords[0])
        lat2 = radians(airport2_coords[0])
        long1 = radians(airport1_coords[1])
        long2 = radians(airport2_coords[1])

        # Reversine formula given by Geeks4Geeks
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

        c = 2 * asin(sqrt(a))
        r = 6371

        return int(round(c * r, 0))

    def is_adjacent(self, source_id: int, destination_id: int) -> bool:
        """Check if two vertices are adjacent"""
        src_id_index = self._edge_indices[source_id]
        dest_id_index = self._edge_indices[destination_id]

        return self._edges[src_id_index][dest_id_index] != 0

    def is_connected(self, source_id: int, destination_id: int, visited: set[int] = None) -> bool:
        """Check if two vertices are connected"""
        if visited is None:
            visited = set()

        if source_id == destination_id:
            return True

        visited.add(source_id)

        for neighbour in self.get_neighbours(source_id):
            if neighbour not in visited:
                if self.is_connected(neighbour, destination_id, visited):
                    return True

        return False

    def __contains__(self, airport_id: int) -> bool:
        """Check if an airport is in the graph"""
        return airport_id in self._vertices

    def __iter__(self):
        """Iterate through the airport objects"""
        return iter(self._vertices.values())

    def __len__(self):
        """Get the number of vertices in the graph"""
        return len(self._vertices)

    def to_networkx(self, max_vertices: int = 100) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(
                v.name, latitude=v.coordinates[0], longitude=v.coordinates[1])

            for u in self.get_neighbours(v.id):
                u_vertex = self._vertices[u]
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u_vertex.name, latitude=u_vertex.coordinates[0],
                                      longitude=u_vertex.coordinates[1])

                if u_vertex.name in graph_nx.nodes:
                    ind1 = self._edge_indices[u_vertex.id]
                    ind2 = self._edge_indices[v.id]
                    distance = self._edges[ind1][ind2]
                    graph_nx.add_edge(v.name, u_vertex.name, weight=distance)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def get_close_airports(self, airport_ids: list[int], max_distance: int) -> list[int]:
        """Get a dictionary of airports within max_distance from the given airport ids"""
        # List check
        for airport_id in airport_ids:
            if airport_id not in self._vertices:
                raise KeyError(
                    f"Airport ID {airport_id} not found in the graph.")

        close_airports = [v for v in self.get_neighbours(
            airport_ids[0]) if self.get_distance(airport_ids[0], v) <= max_distance]
        for airport_id in airport_ids[1:]:
            close_airports = [v for v in close_airports if self.get_distance(
                airport_id, v) <= max_distance]
        return close_airports


# TODO: SAFETY INDEX
def load_airports_graph(df1: pd.DataFrame, df2: pd.DataFrame) -> AirportsGraph:
    """Given two pandas DataFrame objects airports and routes, build and return an airport graph using the data

    Preconditions:
    - df1 is a valid airports dataframe
    - df2 is a valid routes dataframe with the routes between airports that exist in df1

    Note:
        Our implementation may look a bit unorganized due to indexing the rows, but this is a faster alternative to
        iterating through dataframe objects.
    """

    airports_graph = AirportsGraph()

    # Create vertices using itertuples instead of to_dict
    for row in df1.itertuples(index=False):
        airport_id = row[0]  # This corresponds to 'Airport ID'
        current_item = _AirportVertex(airport_id, row[1], row[6], (row[4], row[5]),
                                      Location(row[2], row[3], row[7]))
        airports_graph.add_vertex(airport_id, current_item)

    # Create edges for routes using itertuples
    for row in df2.itertuples(index=False):
        source_airport_id = row[3]  # This corresponds to 'Source airport ID'
        # This corresponds to 'Destination airport ID'
        destination_airport_id = row[5]

        # Ensure both airports exist in the airports dataframe
        if source_airport_id in airports_graph and destination_airport_id in airports_graph:
            airports_graph.add_edge(source_airport_id, destination_airport_id)

    return airports_graph


if __name__ == "__main__":
    # import doctest

    # doctest.testmod()

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': ["pandas", "networkx", "visualizer"],  # the names (strs) of imported modules
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length':` 120
    # })

    from visualizer import visualize_graph

    # airports_data = "data/airports_small.dat"
    # routes_data = "data/routes_small.dat"

    airports_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    routes_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

    safety_data = "data/safest-countries-in-the-world-2025.csv"

    airports_df, routes_df, safety_df = load_data(
        airports_data, routes_data, safety_data)

    g = load_airports_graph(airports_df, routes_df)

    visualize_graph(g)

    # Testing
    # print(g.get_neighbours(1))

    # print(g.is_connected(1, 2))
