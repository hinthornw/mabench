from contextlib import ContextVar
from typing import Dict, Any

data: ContextVar[Dict[str, Any]] = ContextVar("data")


def get_data():
    return data.get()

def set_data(data: Dict[str, Any]):
    return data.set(data)
