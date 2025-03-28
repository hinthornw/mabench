"""Adapted from τ-bench https://arxiv.org/abs/2406.12045"""

import json
from mabench.utils import get_data


def get_order_details(order_id: str) -> str:
    """
    Get the status and details of an order.

    Args:
        order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol
                 at the beginning of the order id.

    Returns:
        A JSON string containing the order details, or an error message if not found.
    """
    data = get_data()
    orders = data["orders"]
    if order_id in orders:
        return json.dumps(orders[order_id])
    return "Error: order not found"
