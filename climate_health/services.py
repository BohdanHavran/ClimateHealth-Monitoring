"""Business operations shared by the versioned API, independent of HTTP."""

from .fuzzy import clamp_inputs, compute_hri
from .validation import finite_number


def analyze_hri(payload):
    keys = {"avg_temp", "solar", "humidity"}
    if not isinstance(payload, dict) or set(payload) != keys:
        raise ValueError("Потрібні рівно avg_temp, solar, humidity")
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float)) for value in payload.values()
    ):
        raise ValueError("Кліматичні показники мають бути JSON-числами")
    original = {
        key: finite_number(payload[key], key, *bounds)
        for key, bounds in {
            "avg_temp": (-100, 70),
            "solar": (0, 1600),
            "humidity": (0, 100),
        }.items()
    }
    effective = clamp_inputs(original)
    return {
        "hri": compute_hri(effective),
        "inputs": original,
        "effective_inputs": effective,
        "clipped": effective != original,
        "method": "fuzzy_rules_27",
        "medical_prediction": False,
    }
