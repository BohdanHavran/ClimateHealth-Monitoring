import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from .validation import finite_number
from threading import RLock


def build_fis_system():
    """
    TrapMF дає покриття на межах (без ситуації "всі membership=0").
    """
    avg_temp = ctrl.Antecedent(np.arange(-5, 36, 1), "avg_temp")
    solar = ctrl.Antecedent(np.arange(60, 301, 1), "solar")
    humidity = ctrl.Antecedent(np.arange(30, 101, 1), "humidity")
    hri = ctrl.Consequent(np.arange(0, 1.01, 0.01), "hri")

    avg_temp["low"] = fuzz.trapmf(avg_temp.universe, [-5, -5, 0, 10])
    avg_temp["medium"] = fuzz.trapmf(avg_temp.universe, [5, 12, 18, 25])
    avg_temp["high"] = fuzz.trapmf(avg_temp.universe, [20, 28, 35, 35])

    solar["low"] = fuzz.trapmf(solar.universe, [60, 60, 110, 160])
    solar["medium"] = fuzz.trapmf(solar.universe, [140, 180, 210, 240])
    solar["high"] = fuzz.trapmf(solar.universe, [220, 255, 300, 300])

    humidity["low"] = fuzz.trapmf(humidity.universe, [30, 30, 40, 60])
    humidity["medium"] = fuzz.trapmf(humidity.universe, [50, 60, 70, 85])
    humidity["high"] = fuzz.trapmf(humidity.universe, [75, 88, 100, 100])

    hri["low"] = fuzz.trapmf(hri.universe, [0.0, 0.0, 0.15, 0.30])
    hri["medium"] = fuzz.trapmf(hri.universe, [0.25, 0.40, 0.60, 0.75])
    hri["high"] = fuzz.trapmf(hri.universe, [0.70, 0.85, 1.0, 1.0])

    rules = []
    terms = ["low", "medium", "high"]
    for t_idx, t in enumerate(terms):
        for s_idx, s in enumerate(terms):
            for h_idx, hh in enumerate(terms):
                score = t_idx + s_idx + h_idx
                out = "low" if score <= 2 else "medium" if score <= 4 else "high"
                rules.append(ctrl.Rule(avg_temp[t] & solar[s] & humidity[hh], hri[out]))

    return ctrl.ControlSystem(rules)


FIS_SYSTEM = build_fis_system()
_LOCK = RLock()


def new_fis_sim():
    return ctrl.ControlSystemSimulation(FIS_SYSTEM)


def clamp_inputs(inputs):
    # Physical validity and HRI model bounds are separate: the existing
    # clipped HRI domain is preserved, but NaN/Inf must never enter inference.
    return {
        "avg_temp": float(
            np.clip(finite_number(inputs["avg_temp"], "temperature", -100, 70), -5, 35)
        ),
        "solar": float(np.clip(finite_number(inputs["solar"], "solar", 0, 1600), 60, 300)),
        "humidity": float(np.clip(finite_number(inputs["humidity"], "humidity", 0, 100), 30, 100)),
    }


def _compute_hri(inputs):
    sim = new_fis_sim()
    sim.input["avg_temp"] = float(inputs["avg_temp"])
    sim.input["solar"] = float(inputs["solar"])
    sim.input["humidity"] = float(inputs["humidity"])
    sim.compute()

    hri_value = sim.output.get("hri")
    if hri_value is None or (isinstance(hri_value, float) and np.isnan(hri_value)):
        raise ValueError(f"HRI не розраховано. inputs={inputs}")
    return float(hri_value)


def compute_hri(inputs):
    with _LOCK:
        return _compute_hri(inputs)
