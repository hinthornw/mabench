"""Adapted from τ-bench https://arxiv.org/abs/2406.12045"""

import json
from typing import Any, Dict


def list_all_airports(data: Dict[str, Any]) -> str:
    """
    List all airports and their cities.
    
    Args:
        data: The data dictionary (not used in this function).
        
    Returns:
        A JSON string mapping airport codes to city names.
    """
    airports = [
        "SFO",
        "JFK",
        "LAX",
        "ORD",
        "DFW",
        "DEN",
        "SEA",
        "ATL",
        "MIA",
        "BOS",
        "PHX",
        "IAH",
        "LAS",
        "MCO",
        "EWR",
        "CLT",
        "MSP",
        "DTW",
        "PHL",
        "LGA",
    ]
    cities = [
        "San Francisco",
        "New York",
        "Los Angeles",
        "Chicago",
        "Dallas",
        "Denver",
        "Seattle",
        "Atlanta",
        "Miami",
        "Boston",
        "Phoenix",
        "Houston",
        "Las Vegas",
        "Orlando",
        "Newark",
        "Charlotte",
        "Minneapolis",
        "Detroit",
        "Philadelphia",
        "LaGuardia",
    ]
    return json.dumps({airport: city for airport, city in zip(airports, cities)})
