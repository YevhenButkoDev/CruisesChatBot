import unittest
from unittest.mock import patch, MagicMock
from src.agent_tools.advanced_api_search import search_cruises, _convert_to_request_params


class TestAdvancedApiSearch(unittest.TestCase):

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_type_id')
    @patch('src.agent_tools.advanced_api_search.get_port_id')
    def test_search_cruises_basic_parameters(self, mock_port_id, mock_type_id, mock_extract, mock_get):
        """Test basic cruise search with minimal parameters"""
        mock_type_id.return_value = 51
        mock_port_id.return_value = 101
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        result = search_cruises(cruise_type="sea", port_from="Barcelona")
        
        # Should be called once for the main API call
        self.assertEqual(mock_get.call_count, 1)
        mock_extract.assert_called_once_with([])
        self.assertEqual(result, [])

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_type_id')
    @patch('src.agent_tools.advanced_api_search.get_port_id')
    def test_search_cruises_with_type_and_ports(self, mock_port_id, mock_type_id, mock_extract, mock_get):
        """Test search with cruise type and port parameters"""
        mock_type_id.return_value = 1
        mock_port_id.side_effect = [101, 102]
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(cruise_type="sea", port_from="Barcelona", port_to="Rome")
        
        mock_type_id.assert_called_once_with("sea")
        self.assertEqual(mock_port_id.call_count, 2)
        mock_port_id.assert_any_call("Barcelona")
        mock_port_id.assert_any_call("Rome")

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_river_id')
    def test_search_cruises_with_rivers(self, mock_river_id, mock_extract, mock_get):
        """Test search with river cruise parameters"""
        mock_river_id.side_effect = [201, 202]
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(rivers=["Rhine", "Danube"])
        
        self.assertEqual(mock_river_id.call_count, 2)
        mock_river_id.assert_any_call("Rhine")
        mock_river_id.assert_any_call("Danube")

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_city_id')
    def test_search_cruises_with_cities(self, mock_city_id, mock_extract, mock_get):
        """Test search with cities to visit"""
        mock_city_id.side_effect = [301, 302, 303]
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(cities_to_visit=["Naples", "Santorini", "Dubrovnik"])
        
        self.assertEqual(mock_city_id.call_count, 3)
        mock_city_id.assert_any_call("Naples")
        mock_city_id.assert_any_call("Santorini")
        mock_city_id.assert_any_call("Dubrovnik")

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_country_id')
    def test_search_cruises_with_countries(self, mock_country_id, mock_extract, mock_get):
        """Test search with departure and destination countries"""
        mock_country_id.side_effect = [401, 402]
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(country_from="Spain", country_to="Italy")
        
        self.assertEqual(mock_country_id.call_count, 2)
        mock_country_id.assert_any_call("Spain")
        mock_country_id.assert_any_call("Italy")

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.datetime')
    def test_search_cruises_with_dates(self, mock_datetime, mock_extract, mock_get):
        """Test search with date parameters"""
        mock_datetime.now.return_value.strftime.return_value = "2025-01-01"
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(time_from_date="2025-06-15", time_to_date="2025-08-31")
        
        # Verify URL contains date parameters
        call_args = mock_get.call_args[0][0]
        self.assertIn("time.fromDate=2025-06-15", call_args)
        self.assertIn("time.toDate=2025-08-31", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    def test_search_cruises_with_duration(self, mock_extract, mock_get):
        """Test search with duration parameter"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(time_duration=3)
        
        call_args = mock_get.call_args[0][0]
        self.assertIn("time.durations=3", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    def test_search_cruises_with_price_range(self, mock_extract, mock_get):
        """Test search with price parameters"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(price_min=500, price_max=2000)
        
        call_args = mock_get.call_args[0][0]
        self.assertIn("price.price=500", call_args)
        self.assertIn("price.maxPrice=2000", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_type_id')
    @patch('src.agent_tools.advanced_api_search.get_river_id')
    @patch('src.agent_tools.advanced_api_search.get_port_id')
    @patch('src.agent_tools.advanced_api_search.get_city_id')
    @patch('src.agent_tools.advanced_api_search.get_country_id')
    def test_search_cruises_all_parameters(self, mock_country_id, mock_city_id, mock_port_id, 
                                         mock_river_id, mock_type_id, mock_extract, mock_get):
        """Test search with all parameters"""
        mock_type_id.return_value = 1
        mock_river_id.return_value = 201
        mock_port_id.side_effect = [101, 102]
        mock_city_id.return_value = 301
        mock_country_id.side_effect = [401, 402]
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(
            cruise_type="river",
            rivers=["Rhine"],
            port_from="Amsterdam",
            port_to="Basel",
            cities_to_visit=["Cologne"],
            country_from="Netherlands",
            country_to="Switzerland",
            time_duration=2,
            time_from_date="2025-05-01",
            time_to_date="2025-09-30",
            price_min=1000,
            price_max=3000
        )
        
        call_args = mock_get.call_args[0][0]
        self.assertIn("cruiseType[]=1", call_args)
        self.assertIn("rivers[]=201", call_args)
        self.assertIn("location.ports[]=101", call_args)
        self.assertIn("location.lastPorts[]=102", call_args)
        self.assertIn("location.cities[]=301", call_args)
        self.assertIn("location.countries[]=401", call_args)
        self.assertIn("location.countriesTo[]=402", call_args)
        self.assertIn("time.fromDate=2025-05-01", call_args)
        self.assertIn("time.toDate=2025-09-30", call_args)
        self.assertIn("time.durations=2", call_args)
        self.assertIn("price.price=1000", call_args)
        self.assertIn("price.maxPrice=3000", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    def test_search_cruises_duration_categories(self, mock_extract, mock_get):
        """Test search with different duration categories"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        # Test each duration category
        duration_categories = [0, 1, 2, 3, 4, 5, 6]
        for duration in duration_categories:
            with self.subTest(duration=duration):
                search_cruises(time_duration=duration)
                call_args = mock_get.call_args[0][0]
                self.assertIn(f"time.durations={duration}", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_type_id')
    def test_search_cruises_sea_vs_river(self, mock_type_id, mock_extract, mock_get):
        """Test search with different cruise types"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        # Test sea cruise
        mock_type_id.return_value = 51
        search_cruises(cruise_type="sea")
        mock_type_id.assert_called_with("sea")
        
        # Test river cruise
        mock_type_id.return_value = 52
        search_cruises(cruise_type="river")
        mock_type_id.assert_called_with("river")

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_river_id')
    def test_search_cruises_multiple_rivers(self, mock_river_id, mock_extract, mock_get):
        """Test search with multiple rivers"""
        mock_river_id.side_effect = [201, 202, 203, 204]
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(rivers=["Rhine", "Danube", "Seine", "Nile"])
        
        call_args = mock_get.call_args[0][0]
        self.assertIn("rivers[]=201&rivers[]=202&rivers[]=203&rivers[]=204", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.get_city_id')
    def test_search_cruises_multiple_cities(self, mock_city_id, mock_extract, mock_get):
        """Test search with multiple cities to visit"""
        mock_city_id.side_effect = [301, 302, 303, 304, 305]
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(cities_to_visit=["Naples", "Santorini", "Dubrovnik", "Barcelona", "Rome"])
        
        call_args = mock_get.call_args[0][0]
        self.assertIn("location.cities[]=301&location.cities[]=302&location.cities[]=303&location.cities[]=304&location.cities[]=305", call_args)

    def test_convert_to_request_params_single_value(self):
        """Test parameter conversion for single values"""
        result = _convert_to_request_params("test_param", "value")
        self.assertEqual(result, "test_param=value")

    def test_convert_to_request_params_list_values(self):
        """Test parameter conversion for list values"""
        result = _convert_to_request_params("test_param[]", [1, 2, 3])
        self.assertEqual(result, "test_param[]=1&test_param[]=2&test_param[]=3")

    def test_convert_to_request_params_empty_list(self):
        """Test parameter conversion for empty list"""
        result = _convert_to_request_params("test_param[]", [])
        self.assertIsNone(result)

    def test_convert_to_request_params_none_value(self):
        """Test parameter conversion for None value"""
        result = _convert_to_request_params("test_param", None)
        self.assertIsNone(result)

    def test_convert_to_request_params_list_with_none_values(self):
        """Test parameter conversion for list with None values"""
        result = _convert_to_request_params("test_param[]", [1, None, 3])
        self.assertEqual(result, "test_param[]=1&test_param[]=3")

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    @patch('src.agent_tools.advanced_api_search.datetime')
    def test_search_cruises_default_from_date(self, mock_datetime, mock_extract, mock_get):
        """Test that default from_date is set to current date when not provided"""
        mock_datetime.now.return_value.strftime.return_value = "2025-12-17"
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises()
        
        call_args = mock_get.call_args[0][0]
        self.assertIn("time.fromDate=2025-12-17", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    def test_search_cruises_no_parameters(self, mock_extract, mock_get):
        """Test search with no parameters"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        result = search_cruises()
        
        mock_get.assert_called_once()
        self.assertEqual(result, [])

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    def test_search_cruises_url_construction(self, mock_extract, mock_get):
        """Test that URL is constructed correctly"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        search_cruises(price_min=1000)
        
        call_args = mock_get.call_args[0][0]
        self.assertTrue(call_args.startswith('https://center.cruises/api/chatbot/cruises/batch-data?'))
        self.assertIn("price.price=1000", call_args)

    @patch('src.agent_tools.advanced_api_search.requests.get')
    @patch('src.agent_tools.advanced_api_search.extract_cruise_summary')
    def test_search_cruises_edge_case_prices(self, mock_extract, mock_get):
        """Test search with edge case price values"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        mock_extract.return_value = []

        # Test with zero prices
        search_cruises(price_min=0, price_max=0)
        call_args = mock_get.call_args[0][0]
        self.assertIn("price.price=0", call_args)
        self.assertIn("price.maxPrice=0", call_args)

        # Test with very high prices
        search_cruises(price_min=50000, price_max=100000)
        call_args = mock_get.call_args[0][0]
        self.assertIn("price.price=50000", call_args)
        self.assertIn("price.maxPrice=100000", call_args)


if __name__ == '__main__':
    unittest.main()
