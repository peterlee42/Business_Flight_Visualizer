"""Our graph ADT"""

from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Any, Union

import networkx as nx
import pandas as pd

from airports_data import load_data


@dataclass
class Airport:
    """DataClass representing information about a given airport.

    Instance Attributes:
        - name: The name of an airport
        - city: The city of the location
        - country: The country for the location
        - coordinates: The coordinates of an airport on map using longitude and latitude
        - timezone: The timezone for the location

    Representation Invariants:
        - self.name != ''
        - self.coordinates != tuple()
        - self.city != ''
        - self.country != ''
        - self.timezone != ''
    """

    name: str
    city: str
    country: str
    coordinates: tuple[float, float]
    timezone: str


class _AirportVertex:
    """Airport Vertex Class

    Instance Attributes:
        - id: The given OpenFlights id of an airport
        - item: The characteristics of the airport vertex
        - global_peace_index: The global peace index of the country that the airport is in. We consider this as the
            "vertex weight."
        - neighbours: The airport vertices that are adjacent to this vertex, and their corresponding edge weights.

    Representation Invariants:
        - self.id >= 0
        - self.global_peace_index >= 0
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """

    id: int
    item: Airport
    global_peace_index: float
    neighbours: dict[_AirportVertex, Union[int, float]]

    def __init__(self, airport_id: int, item: Airport, global_peace_index: float) -> None:
        self.id = airport_id
        self.item = item
        self.global_peace_index = global_peace_index
        self.neighbours = {}

    def get_degree(self) -> int:
        """Return the degree of this vertex"""
        return len(self.neighbours)


class AirportsGraph:
    """A weighted graph used to represent airport connections and the distances of the distance of each route"""

    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps airport id to _Vertex object.

    _vertices: dict[Any, _AirportVertex]

    def __init__(self) -> None:
        self._vertices = {}

    def add_vertex(self, airport_id: int, item: Airport, global_peace_index: float) -> None:
        """Add an airport to the graph, mapping the airport id to the vertex object"""
        if airport_id not in self._vertices:
            self._vertices[airport_id] = _AirportVertex(airport_id, item, global_peace_index)

    def add_edge(self, source_id: int, destination_id: int) -> None:
        """Add an adjacent airport and its distance to this vertex. Since the graph is not oriented, we also add the
        reverse edge.

        Preconditions:
            - source_id != destination_id
        """
        if source_id in self._vertices and destination_id in self._vertices:
            # Since the graph is not oriented, the edges will be symmetric.
            source_vertex = self._vertices[source_id]
            destination_vertex = self._vertices[destination_id]

            # case if edge already exists, we don't need to recalculate distance to improve runtime.
            if source_vertex in destination_vertex.neighbours or destination_vertex in source_vertex.neighbours:
                return
            else:
                distance = self.get_earth_distance(source_id, destination_id)

                source_vertex.neighbours[destination_vertex] = distance
                destination_vertex.neighbours[source_vertex] = distance
        else:
            raise KeyError("Source ID or Destination ID do not exist in this graph.")

    def get_neighbours(self, airport_id: int) -> set[int]:
        """Return a set of airport ids that are adjacent to the vertex corresponding to the given airport id.
        If the id does not exist, raise a Value Error.
        """
        if airport_id in self._vertices:
            return {neighbour.id for neighbour in self._vertices[airport_id].neighbours}
        else:
            raise ValueError("The given airport id does not exist.")

    def get_earth_distance(self, airport_id1: int, airport_id2: int) -> int:
        """Return the rounded integer distance (in kilometers) between the given two airports

        Credits to Geeks4Geeks for inspiration.
        """
        airport1_coords = self._vertices[airport_id1].item.coordinates
        airport2_coords = self._vertices[airport_id2].item.coordinates

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

    def is_connected(self, source_id: int, destination_id: int, visited: set[int]) -> bool:
        """Check if two vertices are connected"""
        if visited is set():
            visited = set()

        if source_id == destination_id:
            return True

        visited.add(source_id)

        for neighbour in self.get_neighbours(source_id):
            if neighbour not in visited:
                if self.is_connected(neighbour, destination_id, visited):
                    return True

        return False

    def get_distance(self, id1: int, id2: int) -> float:
        """Return the distance between the corresponding vertices with id1 and id2.
        Raise a ValueError if either id does not exist."""
        if id1 in self._vertices and id2 in self._vertices:
            v1 = self._vertices[id1]
            v2 = self._vertices[id2]
            return v1.neighbours.get(v2, 0)
        else:
            raise ValueError("No distance given between these two airports.")

    def get_airport_names_from_id(self, airport_ids: list[int]) -> list[str]:
        """Return the corresponding airport names given a list of airport ids"""
        return [self._vertices[airport].item.name for airport in airport_ids]

    def get_airport_id_from_names(self, airport_names: list[str]) -> list[int]:
        """Return the corresponding airport ids given a list of airport names"""
        return [airport_id for airport_id, airport in self._vertices.items() if airport.item.name in airport_names]

    def __contains__(self, airport_id: int) -> bool:
        """Check if an airport is in the graph"""
        return airport_id in self._vertices

    def __iter__(self) -> iter:
        """Iterate through the airport objects"""
        return iter(self._vertices.values())

    def __len__(self) -> int:
        """Get the number of vertices in the graph"""
        return len(self._vertices)

    def to_networkx(self, max_vertices: int = 7000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        This code has been inspired by the method built in exercise3/exercise4
        """

        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(
                v.item.name,
                latitude=v.item.coordinates[0],
                longitude=v.item.coordinates[1],
                id=v.id,
                global_piece_index=v.global_peace_index,
                country=v.item.country
            )

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(
                        u.item.name,
                        latitude=u.item.coordinates[0],
                        longitude=u.item.coordinates[1],
                        id=u.id,
                        global_piece_index=u.global_peace_index,
                        country=u.item.country
                    )

                if u.item.name in graph_nx.nodes:
                    distance = v.neighbours[u]
                    graph_nx.add_edge(v.item.name, u.item.name, weight=distance)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def get_neighbour_within_dist(self, airport_id: int, max_distance: int) -> set:
        """Get adjacent neighbours that are within max_distance"""
        curr_airport_vertex = self._vertices[airport_id]
        return {neighbour.id for neighbour in curr_airport_vertex.neighbours if
                curr_airport_vertex.neighbours[neighbour] <= max_distance}

    def dfs_for_distance(self, airport_id: int, max_distance: int,
                         airports_in_dist: set[int]) -> None:
        """Use Depth First Search Algorithm to find all aiports within a distance."""
        if max_distance < 0 or airport_id in airports_in_dist:
            return
        else:
            airports_in_dist.add(airport_id)
            for neighbour, edge_weight in self._vertices[airport_id].neighbours.items():
                self.dfs_for_distance(neighbour.id, max_distance - edge_weight, airports_in_dist)

    def get_connected_within_dist(self, airport_id: int, max_distance: int) -> set[int]:
        """Get any connected vertex from the airport corresponding to airport_id where there exists a path that is
        less than or equal to max_distance distance."""
        if airport_id not in self._vertices:
            return set()
        else:
            airports_in_dist = set()
            self.dfs_for_distance(airport_id, max_distance, airports_in_dist)
            return airports_in_dist

    def get_close_airports_adjacent(self, airport_ids: list[int], max_distance: int) -> set:
        """Return a set of airport ids that are adjacent to every airport in airport_ids within max_distance.

        Preconditions:
            - all({airport_id in self._vertices for airport_id in airport_ids})
        """
        # Compute the neighbours that are at most max_distance far for the first id.
        close_airports = self.get_neighbour_within_dist(airport_ids[0], max_distance)

        # Then we can find the intersection of all airports that are at most max_distance away from all airports.
        for airport_id in airport_ids[1:]:
            close_airports = close_airports.intersection(self.get_neighbour_within_dist(airport_id, max_distance))

        return close_airports

    def get_close_airports_connected(self, airport_ids: list[int], max_distance: int) -> set:
        """Return a set of airport ids that are connected to every airport in airport_ids. Each of these airports must
         have a route/path within max_distance far.

        Preconditions:
            - all({airport_id in self._vertices for airport_id in airport_ids})
        """
        # Compute the neighbours that are at most max_distance far for the first id.
        close_airports = self.get_connected_within_dist(airport_ids[0], max_distance)

        # Then we can find the intersection of all airports that are at most max_distance away from all airports.
        for airport_id in airport_ids[1:]:
            close_airports = close_airports.intersection(self.get_connected_within_dist(airport_id, max_distance))

        return close_airports

    def rank_airports(self, airport_ids: set[int], max_out_size: int) -> list[int]:
        """Rank the airports by their global peace index and number of connections.
        Group each airport by the ones in the same country and keep the ones with the highest connections.
        Then, rank each country by their global peace index, and finally rank by combining the two.

        Preconditions:
            - all({airport_id in self._vertices for airport_id in airport_ids})
        """
        countries = {}
        for airport_id in airport_ids:
            airport_vertex = self._vertices[airport_id]
            country = airport_vertex.item.country
            if country not in countries:
                countries[country] = []
            countries[country].append(airport_id)

        for country in countries:
            countries[country] = sorted(airport_ids, key=lambda given_id: self._vertices[given_id].get_degree(),
                                        reverse=True)[:max_out_size]

        # Rank the countries by their Global Peace Index and merge the lists together
        ranked_airports = []
        for country in sorted(countries,
                              key=lambda given_id: self._vertices[countries[given_id][0]].global_peace_index):
            ranked_airports += countries[country]

        return ranked_airports[:max_out_size]


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
        airport_item = Airport(row[1], row[2], row[3], (row[4], row[5]), row[6])
        airport_gpi = row[8]
        airports_graph.add_vertex(airport_id, airport_item, airport_gpi)

    # Create edges for routes using itertuples
    for row in df2.itertuples(index=False):
        source_airport_id = row[1]  # This corresponds to 'Source airport ID'
        # This corresponds to 'Destination airport ID'
        destination_airport_id = row[3]

        # Ensure both airports exist in the airports dataframe
        if source_airport_id in airports_graph and destination_airport_id in airports_graph:
            airports_graph.add_edge(source_airport_id, destination_airport_id)

    return airports_graph


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["pandas", "networkx", "visualizer", "math", "airports_data"],
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })

    from visualizer import visualize_graph, visualize_graph_app

    small_airports_data = "data/airports_small.dat"
    small_routes_data = "data/routes_small.dat"

    airports_data = "data/airports.csv"
    routes_data = "data/routes.csv"

    gpi_data = "data/Global Peace Index 2023.csv"

    # ----------Our heatmap visualizer for big data----------
    airports_df, routes_df = load_data(airports_data, routes_data, gpi_data)
    airports_graph_full = load_airports_graph(airports_df, routes_df)
    visualize_graph(airports_graph_full)

    # ----------Our Interactive visualizer app for small data----------
    small_airports_df, small_routes_df = load_data(small_airports_data, small_routes_data, gpi_data)
    small_airports_graph = load_airports_graph(small_airports_df, small_routes_df)
    visualize_graph_app(small_airports_graph)
