import pandas as pd


def calculate_mission_score(
    solar_score,
    terrain_score,
    safety_score
):

    weights = {
        "Solar": 0.30,
        "Terrain": 0.40,
        "Safety": 0.30
    }

    overall_score = (
        solar_score * weights["Solar"]
        + terrain_score * weights["Terrain"]
        + safety_score * weights["Safety"]
    )

    return round(overall_score, 2)


def rank_landing_sites(sites):

    results = []

    for site in sites:

        score = calculate_mission_score(
            site["solar_score"],
            site["terrain_score"],
            site["safety_score"]
        )

        results.append({
            "Landing Site": site["name"],
            "Solar Score": site["solar_score"],
            "Terrain Score": site["terrain_score"],
            "Safety Score": site["safety_score"],
            "Overall Score": score
        })

    results = sorted(
        results,
        key=lambda x: x["Overall Score"],
        reverse=True
    )

    for rank, site in enumerate(results, start=1):
        site["Rank"] = rank

    return pd.DataFrame(results)