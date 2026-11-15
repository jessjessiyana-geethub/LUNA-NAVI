

import unittest

from modules.mission_scoring import (
    calculate_mission_score,
    rank_landing_sites,
    MISSION_SCENARIOS
)


class TestMissionComparison(unittest.TestCase):

    def setUp(self):
        self.sites = [
            {
                "name": "Site A",
                "solar_score": 80,
                "communication_score": 70,
                "terrain_score": 90,
                "safety_score": 85
            },
            {
                "name": "Site B",
                "solar_score": 75,
                "communication_score": 90,
                "terrain_score": 70,
                "safety_score": 80
            },
            {
                "name": "Site C",
                "solar_score": 90,
                "communication_score": 60,
                "terrain_score": 85,
                "safety_score": 95
            }
        ]

    def test_calculate_mission_score(self):
        score = calculate_mission_score(
            solar_score=80,
            communication_score=70,
            terrain_score=90,
            safety_score=85,
            scenario="Balanced"
        )

        self.assertEqual(score, 81.75)

    def test_rank_landing_sites(self):
        results = rank_landing_sites(
            self.sites,
            scenario="Balanced"
        )

        self.assertEqual(
    results.iloc[0]["Landing Site"],
    "Site C"
)

        self.assertEqual(
            list(results["Rank"]),
            [1, 2, 3]
        )

    def test_solar_focused_scenario(self):
        score = calculate_mission_score(
            100, 0, 0,
            communication_score=0,
            scenario="Solar-focused"
        )

        self.assertEqual(score, 50.0)

    def test_communication_focused_scenario(self):
        score = calculate_mission_score(
            0, 0, 0,
            communication_score=100,
            scenario="Communication-focused"
        )

        self.assertEqual(score, 50.0)

    def test_score_range(self):
        score = calculate_mission_score(
            100, 100, 100,
            communication_score=100,
            scenario="Balanced"
        )

        self.assertEqual(score, 100.0)

    def test_invalid_scenario(self):
        with self.assertRaises(ValueError):
            calculate_mission_score(
                80, 90, 85,
                communication_score=70,
                scenario="Unknown"
            )

    def test_invalid_score(self):
        with self.assertRaises(ValueError):
            calculate_mission_score(
                120, 90, 85,
                communication_score=70
            )

    def test_scenario_weights_total_100_percent(self):
        for weights in MISSION_SCENARIOS.values():
            self.assertAlmostEqual(sum(weights.values()), 1.0)


if __name__ == "__main__":
    unittest.main()
