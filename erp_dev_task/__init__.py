__version__ = "0.0.1"

import json


def load_json(data):
    try:
        if isinstance(data, dict):
            return data
        return json.loads(data) if data else {}
    except json.JSONDecodeError:
        return {}