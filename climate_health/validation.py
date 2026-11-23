import math


def finite_number(value, name, low, high):
    """Validate input before any database call, fuzzy clipping or cache lookup."""
    if isinstance(value, bool):
        raise ValueError(f"Некоректне значення: {name}")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"Некоректне значення: {name}") from exc
    if not math.isfinite(number) or not low <= number <= high:
        raise ValueError(f"Значення {name} поза допустимими межами")
    return number


def bounded_integer(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"Некоректне значення: {name}")
    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"Некоректне значення: {name}") from exc
    if not low <= result <= high:
        raise ValueError(f"Значення {name} поза допустимими межами")
    return result
