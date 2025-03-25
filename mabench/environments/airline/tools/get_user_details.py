"""Adapted from τ-bench https://arxiv.org/abs/2406.12045"""

import json
from mabench.utils import get_data


def get_user_details(user_id: str) -> str:
    """
    Get the details of a user.
    
    Args:
        user_id: The user id, such as 'sara_doe_496'.
        
    Returns:
        A JSON string representing the user details or an error message.
    """
    data = get_data()
    users = data["users"]
    if user_id in users:
        return json.dumps(users[user_id])
    return "Error: user not found"
