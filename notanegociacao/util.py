import json
import datetime
from typing import Any, get_args, get_origin
import re


def strToFloat(value: str) -> float:
    return float(value.replace('.', '').replace(',', '.'))


def strToInt(value: str) -> int:
    return int(value.replace('.', ''))


def extractNumber(text: str) -> float:
    numbers = re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2}", text)

    if not numbers:
        return 0.0

    value = strToFloat(numbers[0])

    if re.search(r"\bD\b\s*$", text):
        value = -value

    return value


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()

        if hasattr(obj, '__dict__'):
            return obj.__dict__

        return super().default(obj)


def from_dict[T](data: Any, cls: type[T]) -> T | datetime.date | list[Any | datetime.date | None] | None:
    if data is None:
        return None

    if cls == datetime.date:
        return datetime.date.fromisoformat(data)

    if get_origin(cls) is list:
        item_type = get_args(cls)[0]
        return [from_dict(item, item_type) for item in data]

    if isinstance(data, dict):
        obj = cls.__new__(cls)

        for field, field_type in cls.__annotations__.items():
            if field in data:
                setattr(
                    obj,
                    field,
                    from_dict(data[field], field_type)
                )

        return obj

    return data
