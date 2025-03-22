"""Our graph ADT"""
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt
from airports_data import airports_df, routes_df


@dataclass
class Location:
    """Location illustrating the city, country, and timezone

    TODO: ADD DESCRIPTION FOR EACH ATTRIBUTE
    Instance Attributes:
    -
    """
    city: str
    country: str
    timezone: str


class _AirportVertex:
    """Airport Vertex Class

    TODO: ADD DESCRIPTION FOR EACH ATTRIBUTE
    Instance Attributes:
    - Coordinates on map using longitude and latitude
    """
    id: int
    name: str
    iata: str
    icao: str
    altitude: int
    coordinates: tuple[float, float]
    location: Location

    def __init__(self, airport_id: int, airport_name: str, airport_iata: str, airport_iaco: str, airport_altitude: int,
                 airport_coordinates: tuple[float, float], airport_location: Location):
        self.id = airport_id
        self.name = airport_name
        self.iata = airport_iata
        self.icao = airport_iaco
        self.altitude = airport_altitude
        self.coordinates = airport_coordinates
        self.location = airport_location


class AirportsGraph:
    """Graph class

    TODO: ADD DOCSTRING
    """

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

    def add_vertex(self, airport_id: int, data: dict[str, Any]) -> None:
        """Add an airport to the graph using its id"""
        if airport_id not in self._vertices:
            self._vertices[airport_id] = _AirportVertex(airport_id, data["Name"], data["IATA"], data["ICAO"],
                                                        data["Altitude"], (data["Latitude"], data["Longitude"]),
                                                        Location(data["City"], data["Country"], data["Timezone"]))

            # add new row of zeroes to make this an nxn matrix
            for row in self._edges:
                row.append(0)
            self._edges.append([0] * (len(self._edges) + 1))  # add another column of zeroes
            self._edge_indices[airport_id] = len(self._edge_indices) - 1

    def add_edge(self, source_id: int, destination_id: int) -> None:
        """Add an edge to the graph"""
        if source_id in self._vertices and destination_id in self._vertices:
            distance = self.get_distance(source_id, destination_id)
            self._edges[self._edge_indices[source_id]][self._edge_indices[destination_id]] = distance
            # self._edges[self._edge_indices[destination_id]][self._edge_indices[source_id]] = distance
        else:
            print('aaa')

    def get_vertex(self, airport_id: int) -> Optional[_AirportVertex]:
        """Get a vertex from the graph"""
        return self._vertices.get(airport_id)

    # def get_neighbours(self, airport_id: int) -> dict[int, _AirportVertex]:
    #     """Get neighbours of a vertex"""
    #     return self._vertices[airport_id].neighbours

    def get_edges(self) -> list[list[int]]:
        """Get all the edges in the graph"""
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

    # def is_adjacent(self, source_id: int, destination_id: int) -> bool:
    #     """Check if two vertices are adjacent"""
    #     return destination_id in self._vertices[source_id].neighbours

    # def is_connected(self, source_id: int, destination_id: int, visited: set[int] = None) -> bool:
    #     """Check if two vertices are connected"""
    #     if visited is None:
    #         visited = set()
    #     visited.add(source_id)  # Add the source vertex to the visited set to avoid cycles
    #     if source_id == destination_id:  # If the source vertex is the destination vertex
    #         return True
    #     for neighbour_id in self._vertices[source_id].neighbours:
    #         if neighbour_id not in visited:
    #             if self.is_connected(neighbour_id, destination_id, visited):
    #                 return True
    #     return False

    def __contains__(self, airport_id: int) -> bool:
        """Check if an airport is in the graph"""
        return airport_id in self._vertices

    def __iter__(self):
        """Iterate through the airport objects"""
        return iter(self._vertices.values())

    def __len__(self):
        """Get the number of vertices in the graph"""
        return len(self._vertices)


def load_airports_graph() -> AirportsGraph:
    """Build a graph"""

    airports_graph = AirportsGraph()

    # Create vertices
    airports_dict = airports_df.to_dict(orient="records")

    for row in airports_dict:
        airports_graph.add_vertex(row["Airport ID"], row)

    # TODO: For now this thing only adds the source and destination routes. Maybe need to encorporate the airlines (?).
    routes_dict = routes_df.to_dict(orient="records")
    for row in routes_dict:
        source_airport_id = row["Source airport ID"]
        destination_airport_id = row["Destination airport ID"]
        if source_airport_id in airports_dict and destination_airport_id in airports_dict:
            airports_graph.add_edge(source_airport_id, destination_airport_id)

    return airports_graph


if __name__ == "__main__":
    pass

    # import doctest

    # doctest.testmod()

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': [],  # the names (strs) of imported modules
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length':` 120
    # })
    g = load_airports_graph()
