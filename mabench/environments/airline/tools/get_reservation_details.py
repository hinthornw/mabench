"""Adapted from τ-bench https://arxiv.org/abs/2406.12045"""

import json
from typing import Any, Dict


def get_reservation_details(data: Dict[str, Any], reservation_id: str) -> str:
    """
    Get the details of a reservation.
    
    Args:
        data: The data dictionary containing reservations information.
        reservation_id: The reservation id, such as '8JX2WO'.
        
    Returns:
        A JSON string representing the reservation details or an error message.
    """
    reservations = data["reservations"]
    if reservation_id in reservations:
        return json.dumps(reservations[reservation_id])
    return "Error: user not found"
