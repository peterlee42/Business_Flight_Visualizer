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
    """
        Vertex class
    """
    airport: Airport

    def __init__(self, airport: Airport):
        self.airport = airport
