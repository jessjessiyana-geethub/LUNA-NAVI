
import pandas as pd


MISSION_SCENARIOS = {
    "Solar-focused": {
        "solar": 0.50,
        "communication": 0.15,
        "terrain": 0.15,
        "safety": 0.20
    },
    "Communication-focused": {
        "solar": 0.15,
        "communication": 0.50,
        "terrain": 0.15,
        "safety": 0.20
    },
    "Balanced": {
        "solar": 0.30,
        "communication": 0.20,
        "terrain": 0.25,
        "safety": 0.25
    }
}


def calculate_mission_score(
    solar_score,
    terrain_score,
    safety_score,
    communication_score=0,
    scenario="Balanced"
):
    scores = {
        "solar": solar_score,
        "communication": communication_score,
        "terrain": terrain_score,
        "safety": safety_score
    }

    if scenario not in MISSION_SCENARIOS:
        raise ValueError("Unknown mission scenario")

    for name, value in scores.items():
        if not isinstance(value, (int, float)) or not 0 <= value <= 100:
            raise ValueError(
                f"{name} score must be between 0 and 100"
            )

    weights = MISSION_SCENARIOS[scenario]

    overall_score = sum(
        scores[key] * weights[key]
        for key in weights
    )

    return round(overall_score, 2)


def rank_landing_sites(
    sites,
    scenario="Balanced"
):
    if scenario not in MISSION_SCENARIOS:
        raise ValueError("Unknown mission scenario")

    results = []

    for site in sites:
        score = calculate_mission_score(
            solar_score=site["solar_score"],
            communication_score=site.get(
                "communication_score", 0
            ),
            terrain_score=site["terrain_score"],
            safety_score=site["safety_score"],
            scenario=scenario
        )

        results.append({
            "Landing Site": site["name"],
            "Solar Score": site["solar_score"],
            "Communication Score": site.get(
                "communication_score", 0
            ),
            "Terrain Score": site["terrain_score"],
            "Safety Score": site["safety_score"],
            "Overall Score": score,
            "Mission Scenario": scenario
        })

    results.sort(
        key=lambda item: item["Overall Score"],
        reverse=True
    )

    for rank, site in enumerate(results, start=1):
        site["Rank"] = rank

    return pd.DataFrame(results)
