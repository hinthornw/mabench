import contextvars
from typing import Any

DATA = contextvars.ContextVar[dict[str, Any] | None]("DATA", default=None)


def get_data():
    result = DATA.get()
    print(f"GETTING DATA: {str(result)[:100]}...")
    return result


def set_data(data: dict[str, Any]):
    print(f"SETTING DATA: {str(data)[:100]}...")
    return DATA.set(data)
