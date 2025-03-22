"""Our graph ADT"""
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass
from airports_data import airports_df, routes_df


@dataclass
class Location:
    """Location illustrating the city, country, and timezone"""
    city: str
    country: str
    timezone: str


@dataclass
class Airport:
    """Airport Item Dataclass

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


class _AirportVertex:
    """Vertex class"""
    airport: Airport

    def __init__(self, airport: Airport):
        self.airport = airport
        self.neighbours = {}  # Neighbours of the vertex

    def get_degree(self) -> int:
        """Get the degree of the vertex"""
        return len(self.neighbours)


class AirportsGraph:
    """Graph class"""

    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.

    _vertices: dict[Any, _AirportVertex]

    def __init__(self):
        self._vertices = {}  # Airport vertices

    def add_vertex(self, airport_id: int, data: dict[str, Any]) -> None:
        """Add an airport to the graph using its id"""
        if airport_id not in self._vertices:
            self._vertices[airport_id] = _AirportVertex(
                Airport(airport_id, data["Name"], data["IATA"], data["ICAO"], data["Altitude"],
                        (data["Latitude"], data["Longitude"]),
                        Location(data["City"], data["Country"], data["Timezone"])))

    def add_edge(self, source_id: int, destination_id: int) -> None:
        """Add an edge to the graph"""
        if source_id in self._vertices and destination_id in self._vertices:
            source_airport = self._vertices[source_id]
            destination_airport = self._vertices[destination_id]
            source_airport.neighbours[destination_id] = destination_airport
            destination_airport.neighbours[source_id] = source_airport

    def get_vertex(self, airport_id: int) -> Optional[_AirportVertex]:
        """Get a vertex from the graph"""
        return self._vertices.get(airport_id)

    def get_neighbours(self, airport_id: int) -> dict[int, _AirportVertex]:
        """Get neighbours of a vertex"""
        return self._vertices[airport_id].neighbours

    def get_edges(self) -> set[tuple[int, int]]:
        """Get all the edges in the graph"""
        edges = set()
        for airport_id, vertex in self._vertices.items():  # Iterate through the vertices
            for neighbour_id in vertex.neighbours:  # Iterate through the neighbours
                edges.add((airport_id, neighbour_id))  # Add the edge to the set
        return edges

    def is_adjacent(self, source_id: int, destination_id: int) -> bool:
        """Check if two vertices are adjacent"""
        return destination_id in self._vertices[source_id].neighbours

    def is_connected(self, source_id: int, destination_id: int, visited: set[int] = None) -> bool:
        """Check if two vertices are connected"""
        if visited is None:
            visited = set()
        visited.add(source_id)  # Add the source vertex to the visited set to avoid cycles
        if source_id == destination_id:  # If the source vertex is the destination vertex
            return True
        for neighbour_id in self._vertices[source_id].neighbours:
            if neighbour_id not in visited:
                if self.is_connected(neighbour_id, destination_id, visited):
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


def load_airports_graph() -> AirportsGraph:
    """Build a graph"""

    airports_graph = AirportsGraph()

    airports_dict = airports_df.to_dict(orient="records")

    for row in airports_dict:
        airports_graph.add_vertex(row["Airport ID"], row)

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
