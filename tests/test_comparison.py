
import unittest

from modules.mission_scoring import (
    calculate_mission_score,
    rank_landing_sites
)


class TestMissionComparison(unittest.TestCase):

    def test_calculate_mission_score(self):

        score = calculate_mission_score(
            solar_score=80,
            terrain_score=90,
            safety_score=85
        )

        self.assertEqual(score, 85.5)

    def test_rank_landing_sites(self):

        sites = [
            {
                "name": "Site A",
                "solar_score": 80,
                "terrain_score": 90,
                "safety_score": 85
            },
            {
                "name": "Site B",
                "solar_score": 75,
                "terrain_score": 70,
                "safety_score": 80
            },
            {
                "name": "Site C",
                "solar_score": 90,
                "terrain_score": 85,
                "safety_score": 95
            }
        ]

        results = rank_landing_sites(sites)

        self.assertEqual(
            results.iloc[0]["Landing Site"],
            "Site C"
        )

        self.assertEqual(
            list(results["Rank"]),
            [1, 2, 3]
        )

    def test_score_range(self):

        score = calculate_mission_score(
            100, 100, 100
        )

        self.assertEqual(score, 100.0)


if __name__ == "__main__":
    unittest.main()
