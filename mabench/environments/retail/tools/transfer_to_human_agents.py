"""Adapted from τ-bench https://arxiv.org/abs/2406.12045"""

from typing import Any, Dict


def transfer_to_human_agents(data: Dict[str, Any], summary: str) -> str:
    """
    Transfer the user to a human agent, with a summary of the user's issue.
    
    Only transfer if the user explicitly asks for a human agent, or if the user's
    issue cannot be resolved by the agent with the available tools.
    
    Args:
        data: The data dictionary (not used in this function).
        summary: A summary of the user's issue.
        
    Returns:
        A confirmation message indicating the transfer was successful.
    """
    # This function simulates the transfer to a human agent.
    return "Transfer successful"
