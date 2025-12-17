import unittest
from src.agent_tools.advanced_api_search import search_cruises


class TestAdvancedApiSearchIntegration(unittest.TestCase):
    """Integration tests that make real HTTP calls to the cruise API"""

    def test_search_sea_cruises(self):
        """Test real API call for sea cruises"""
        result = search_cruises(cruise_type="sea")
        self.assertIsInstance(result, list)
        print(f"Sea cruises found: {len(result)}")

    def test_search_river_cruises(self):
        """Test real API call for river cruises"""
        result = search_cruises(cruise_type="river")
        self.assertIsInstance(result, list)
        print(f"River cruises found: {len(result)}")

    def test_search_with_rivers(self):
        """Test real API call with specific rivers"""
        result = search_cruises(rivers=["Rhine", "Danube"])
        self.assertIsInstance(result, list)
        print(f"Rhine/Danube cruises found: {len(result)}")

    def test_search_with_ports(self):
        """Test real API call with departure port"""
        result = search_cruises(port_from="Barcelona")
        self.assertIsInstance(result, list)
        print(f"Barcelona departure cruises found: {len(result)}")

    def test_search_with_cities(self):
        """Test real API call with cities to visit"""
        result = search_cruises(cities_to_visit=["Naples"])
        self.assertIsInstance(result, list)
        print(f"Naples visit cruises found: {len(result)}")

    def test_search_with_duration(self):
        """Test real API call with duration category"""
        result = search_cruises(time_duration=2)  # 6-9 days
        self.assertIsInstance(result, list)
        print(f"6-9 day cruises found: {len(result)}")

    def test_search_with_dates(self):
        """Test real API call with date range"""
        result = search_cruises(
            time_from_date="2025-06-01",
            time_to_date="2025-08-31"
        )
        self.assertIsInstance(result, list)
        print(f"Summer 2025 cruises found: {len(result)}")

    def test_search_with_price_range(self):
        """Test real API call with price range"""
        result = search_cruises(price_min=500, price_max=2000)
        self.assertIsInstance(result, list)
        print(f"€500-2000 cruises found: {len(result)}")

    def test_search_combined_parameters(self):
        """Test real API call with multiple parameters"""
        result = search_cruises(
            cruise_type="sea",
            port_from="Barcelona",
            time_duration=1,  # 3-5 days
            price_max=1500
        )
        self.assertIsInstance(result, list)
        print(f"Barcelona sea cruises (3-5 days, <€1500): {len(result)}")

    def test_search_all_parameters(self):
        """Test real API call with all parameters"""
        result = search_cruises(
            cruise_type="sea",
            port_from="Miami",
            time_duration=0,  # 1-2 days
            price_min=300,
            price_max=1000
        )
        self.assertIsInstance(result, list)
        print(f"Miami short cruises with all params: {len(result)}")


if __name__ == '__main__':
    unittest.main()
