"""Sample module with basic bloat and dead symbols."""

import json
import os  # Unused import
import sys  # Unused import
from typing import Optional


# This is a very verbose humanoid comment explaining obvious code
def calculate_total(items: list[dict]) -> float:
    """
    Calculate the total price of all items in the shopping cart.
    
    Args:
        items: List of item dictionaries with price and quantity.
    Returns:
        float total price
    """
    total = 0.0
    if items:
        for item in items:
            if "price" in item and "quantity" in item:
                total += float(item["price"]) * int(item["quantity"])
    return total


def dead_utility_function(x: int) -> int:
    """This function is never called or imported anywhere."""
    return x * 42
