'''
Uses openweathermap api to get the weather local to the user
NOTE: This is a slower api and may take upwards of a minute to get the data
'''

import requests


def get_weather(city_name: str, api_key: str):
    '''
    Get the current weatehr for the city using Open Weather Map API
    Returns the temperature (in kelvin), the pressure, humidity
    and current weather description
    '''

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + str(api_key) + "&q=" + str(city_name)

    # print response object
    response = requests.get(complete_url)
    output_json = response.json()

    # Make sure the information is valid if not return an error as it is hard for us to diagnose exactly
    try:
        # Split the json to get the temp, pressure, humidity and weather
        main_branch = output_json["main"]
        current_temperature = main_branch["temp"]
        current_pressure = main_branch["pressure"]
        current_humidiy = main_branch["humidity"]
        weather_branch = output_json["weather"]
        weather_description = weather_branch[0]["description"]
        return current_temperature, current_pressure, \
            current_humidiy, weather_description
    except:
        return "Error city name or api key not valid or the openweather api is offline!"
