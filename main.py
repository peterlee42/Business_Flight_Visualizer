"""Our graph ADT"""
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt

import pandas as pd

from airports_data import load_airport_and_route_data
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
    - id: int
        The airport id
    - name: str
        The airport name
    - iata: str
        The airport IATA code
    - icao: str
        The airport ICAO code
    - altitude: int
        The airport altitude
    - coordinates: tuple[float, float]
        The airport coordinates (latitude, longitude)
    - location: Location
        The airport location (city, country, timezone)
    - _adjacent: dict[Any, float]
        The adjacent airports and their distances, maps airport id to weight (distance)
    - id: The OpenFlights id of an airport
    - name: The name of an airport
    - iata: The IATA code of an airport
    - icao: The ICAO code of an airport
    - altitude: The altitude of an airport
    - coordinates: The coordinates of an airport on map using longitude and latitude
    - location: The location of an airport

    Representation Invariants:
    - self.id >= 0
    - self.name != ''
    - self.iata != ''
    - self.icao != ''
    - self.altitude > 0
    - self.coordinates != tuple()
    """
    id: int
    name: str
    iata: str
    icao: str
    altitude: int
    coordinates: tuple[float, float]
    location: Location
    _adjacent: dict[int, float]

    def __init__(self, airport_id: int, airport_name: str, airport_iata: str, airport_iaco: str, airport_altitude: int,
                 airport_coordinates: tuple[float, float], airport_location: Location):
        self.id = airport_id
        self.name = airport_name
        self.iata = airport_iata
        self.icao = airport_iaco
        self.altitude = airport_altitude
        self.coordinates = airport_coordinates
        self.location = airport_location
        self._adjacent = {}

    def is_adjacent(self, other: _AirportVertex) -> bool:
        """Check if this vertex is adjacent to another vertex"""
        if self.id == other.id:
            return False
        elif self._adjacent.get(other.id) is not None and other._adjacent.get(self.id) is not None:
            return True
        else:
            return False

    def get_neighbours(self) -> set[int]:
        """Return the airport id of neighbours of this vertex"""
        return set(self._adjacent.keys())

    def get_distance(self, other: _AirportVertex) -> float:
        """Return the distance between this vertex and another vertex"""
        if self.id == other.id:
            return 0.0
        elif self._adjacent.get(other.id) is not None:
            return self._adjacent[other.id]
        else:
            raise ValueError("No distance given between these two airports.")
        
    def add_adjacent(self, other: _AirportVertex, distance: float) -> None:
        """Add an adjacent airport and its distance to this vertex. Since the graph is not oriented, we also add the reverse edge."""
        if self.id == other.id:
            raise ValueError("Cannot add an airport to itself.")
        elif other.id in self._adjacent or self.id in other._adjacent:
            raise ValueError("Airport already exists in the adjacent list.")
        else:
            self._adjacent[other.id] = distance
            other._adjacent[self.id] = distance


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

    def __init__(self):
        self._vertices = {}

    def add_vertex(self, airport_id: int, item: _AirportVertex) -> None:
        """Add an airport to the graph, mapping the airport id to the vertex object"""
        if airport_id not in self._vertices:
            self._vertices[airport_id] = item

    def add_edge(self, source_id: int, destination_id: int) -> None:
        """Add an edge to the graph"""
        if source_id in self._vertices and destination_id in self._vertices:
            source_vertex = self.get_vertex(source_id)
            destination_vertex = self.get_vertex(destination_id)
            # case if edge already made from other side to improve speed. we assume 0 means edge does not exist.
            if source_vertex.is_adjacent(destination_vertex):
                raise ValueError("Edge already exists between these two airports.")
            else:
                distance = self.get_earth_distance(source_id, destination_id)

                source_vertex.add_adjacent(destination_vertex, distance)  # Will add the reverse edge as well
        else:
            raise KeyError("Source ID or Destination ID do not exist in this graph.")

    def get_vertex(self, airport_id: int) -> Optional[_AirportVertex]:
        """Return a vertex object from its id"""
        return self._vertices.get(airport_id)

    def get_earth_distance(self, airport_id1: int, airport_id2: int) -> int:
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

    def is_connected(self, source_id: int, destination_id: int, visited: set[int] = None) -> bool:
        """Check if two vertices are connected"""
        if visited is None:
            visited = set()

        if source_id == destination_id:
            return True

        visited.add(source_id)

        for neighbour in self.get_vertex(source_id).get_neighbours():
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

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(
                v.name, latitude=v.coordinates[0], longitude=v.coordinates[1])

            for u in v.get_neighbours():
                u_vertex = self._vertices[u]
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u_vertex.name, latitude=u_vertex.coordinates[0],
                                      longitude=u_vertex.coordinates[1])

                if u_vertex.name in graph_nx.nodes:
                    distance = v.get_distance(u_vertex)
                    graph_nx.add_edge(v.name, u_vertex.name, weight = distance)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx
    
    def get_close_airports(self, airport_ids: list[int], max_distance: int) -> set[int]:
        """Return a set of airport ids within max_distance from the given airport ids"""
        # Input check
        for airport_id in airport_ids:
            if airport_id not in self._vertices:
                raise KeyError(f"Airport ID {airport_id} not found in the graph.")

        close_airports = {neighbour for neighbour in self.get_vertex(airport_ids[0]).get_neighbours() if
            self.get_earth_distance(airport_ids[0], neighbour) <= max_distance}

        for airport_id in airport_ids[1:]:
            close_airports = close_airports.intersection(
                {neighbour for neighbour in self.get_vertex(airport_id).get_neighbours() if
                 self.get_earth_distance(airport_id, neighbour) <= max_distance})
        
        return close_airports


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
        current_item = _AirportVertex(airport_id, row[1], row[4], row[5], row[8],
                                      (row[6], row[7]),
                                      Location(row[2], row[3], row[9]))
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
    #     'extra-imports': [],  # the names (strs) of imported modules
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length':` 120
    # })
    from visualizer import visualize_graph

    airports_data = "data/airports_small.dat"
    routes_data = "data/routes_small.dat"

    # airports_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    # routes_data = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

    airports_df, routes_df = load_airport_and_route_data(
        airports_data, routes_data)

    g = load_airports_graph(airports_df, routes_df)

    visualize_graph(g)

    # Testing
    # print(g.get_neighbours(1))

    # print(g.is_connected(1, 2))
