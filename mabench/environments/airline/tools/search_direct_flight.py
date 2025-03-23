"""Adapted from τ-bench https://arxiv.org/abs/2406.12045"""

import json
from typing import Any, Dict


def search_direct_flight(
    data: Dict[str, Any], origin: str, destination: str, date: str
) -> str:
    """
    Search direct flights between two cities on a specific date.
    
    Args:
        data: The data dictionary containing flight information.
        origin: The origin city airport in three letters, such as 'JFK'.
        destination: The destination city airport in three letters, such as 'LAX'.
        date: The date of the flight in the format 'YYYY-MM-DD', such as '2024-01-01'.
        
    Returns:
        A JSON string containing the list of available flights.
    """
    flights = data["flights"]
    results = []
    for flight in flights.values():
        if flight["origin"] == origin and flight["destination"] == destination:
            if (
                date in flight["dates"]
                and flight["dates"][date]["status"] == "available"
            ):
                # results add flight except dates, but add flight["datas"][date]
                results.append({k: v for k, v in flight.items() if k != "dates"})
                results[-1].update(flight["dates"][date])
    return json.dumps(results)
