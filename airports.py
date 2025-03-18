"""Our graph ADT"""
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass
from airports_data import airports_df, routes_df


@dataclass
class Airport:
    """Airport Item Dataclass"""
    id: int
    name: str
    city: str
    country: str
    iata: str
    icao: str
    latitude: float
    longitude: float
    altitude: int
    timezone: str


class _AirportVertex:
    """Vertex class"""
    airport: Airport

    def __init__(self, airport: Airport):
        self.airport = airport
        self.neighbours = {}  # Neighbours of the vertex

    def get_degree(self) -> int:
        """Get the degree of the vertex"""
        return len(self.neighbours)


class Airports_Graph:
    """Graph class"""
    def __init__(self):
        self._vertices = {}  # Airport vertices

    def add_vertex(self, airport_id: int) -> None:
        """Add an airport to the graph using its id"""
        if airport_id not in self._vertices:
            self._vertices[airport_id] = _AirportVertex(Airport(
                airport_id,
                airports_df.loc[airport_id, "Name"],
                airports_df.loc[airport_id, "City"],
                airports_df.loc[airport_id, "Country"],
                airports_df.loc[airport_id, "IATA"],
                airports_df.loc[airport_id, "ICAO"],
                airports_df.loc[airport_id, "Latitude"],
                airports_df.loc[airport_id, "Longitude"],
                airports_df.loc[airport_id, "Altitude"],
                airports_df.loc[airport_id, "Timezone"]
            ))

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
            for neighbour_id in vertex.neighbours:         # Iterate through the neighbours
                edges.add((airport_id, neighbour_id))      # Add the edge to the set
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