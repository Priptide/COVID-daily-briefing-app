from weather_update import get_weather


def test_api_key():
    assert get_weather(
        "London", "3243423423424") == "Error city name or api key not valid or the openweather api is offline!"


def test_wrong_city():
    assert get_weather(
        "odosfsdo", "1badcdc04f3787dfffa0385872d51f1b") == "Error city name or api key not valid or the openweather api is offline!"


def test_bad_input():
    assert get_weather(
        12345, 12312313) == "Error city name or api key not valid or the openweather api is offline!"


def test_good_input():
    assert get_weather(
        "London", "1badcdc04f3787dfffa0385872d51f1b") != "Error city name or api key not valid or the openweather api is offline!"
