import pytest
from unittest.mock import patch, MagicMock
from logitrack.api_client import WeatherApiClient
from logitrack.services import WeatherShippingService

@patch("logitrack.api_client.requests.get")
def test_weather_api_client_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"current_weather": {"windspeed": 20.0, "temperature": 25.0}}
    mock_get.return_value = mock_response
    client = WeatherApiClient()
    result = client.fetch_weather(32.0, 34.0)
    assert result["current_weather"]["windspeed"] == 20.0

@patch("logitrack.api_client.time.sleep", return_value=None)
@patch("logitrack.api_client.requests.get")
def test_weather_api_client_timeout_retry(mock_get, mock_sleep):
    import requests
    mock_get.side_effect = requests.Timeout("Timeout")
    client = WeatherApiClient(timeout=0.1, max_retries=3)
    with pytest.raises(ConnectionError):
        client.fetch_weather(32.0, 34.0)
    assert mock_get.call_count == 3

@patch.object(WeatherApiClient, "fetch_weather", side_effect=Exception("API Down"))
def test_weather_shipping_service_fallback(mock_fetch, sample_order, sample_vehicle):
    service = WeatherShippingService()
    result = service.evaluate_shipment(sample_order, sample_vehicle, 32.0, 34.0)
    assert result["fallback_mode"] is True
    assert result["is_weight_safe"] is True