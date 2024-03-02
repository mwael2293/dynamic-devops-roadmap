import requests
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        """Tests the root route for a successful response."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Welcome to the Flask app!')

    def test_version(self):
        """Tests the version route for a successful response."""
        response = self.app.get('/version')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'0.0.1')

    @patch('app.requests.get')
    def test_temperature_success(self, mock_get):
        """Tests the temperature route with a successful API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "sensors": [
                {
                    "title": "Temperatur",
                    "lastMeasurement": {
                        "value": 25.5,
                        "createdAt": (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        response = self.app.get('/Temperature')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'temperature': 25.5})

    @patch('app.requests.get')
    def test_temperature_old_data(self, mock_get):
        """Tests the temperature route with outdated data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "sensors": [
                {
                    "title": "Temperatur",
                    "lastMeasurement": {
                        "value": 20.0,
                        "createdAt": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        response = self.app.get('/Temperature')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'Data outdated (exceeds 1 hour)')



    @patch('app.requests.get')
    def test_temperature_api_error(self, mock_get):
        # ... existing mock setup with error raising ...

        mock_get.side_effect = requests.exceptions.RequestException()

        response = self.app.get('/Temperature')
        self.assertEqual(response.status_code, 404)  # Adjust expectation to 500
        self.assertIn(b'Failed to fetch temperature data', response.data)

if __name__ == '__main__':
    unittest.main()
