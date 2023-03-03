import requests

from bot.ai import generate_response
from bot.translate import translate_text

wmo_to_text = [
    ([0],               'Clear sky'),
    ([1, 2, 3],         'Mainly clear, partly cloudy, and overcast'),
    ([45, 48],          'Fog and depositing rime fog'),
    ([51, 53, 55],      'Drizzle: Light, moderate, and dense intensity'),
    ([56, 57],          'Freezing Drizzle: Light and dense intensity'),
    ([61, 63, 65],      'Rain: Slight, moderate and heavy intensity'),
    ([66, 67],          'Freezing Rain: Light and heavy intensity'),
    ([71, 73, 75],      'Snow fall: Slight, moderate, and heavy intensity'),
    ([77],              'Snow grains'),
    ([80, 81, 82],      'Rain showers: Slight, moderate, and violent'),
    ([85, 86],          'Snow showers slight and heavy'),
    ([95],              'Thunderstorm: Slight or moderate'),
    ([96, 99],          'Thunderstorm with slight and heavy hail'),
]

places = [
    {'name': 'Kyiv', 'params': {'latitude': '50.45', 'longitude': '30.52', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': 'London', 'params': {'latitude': '51.51', 'longitude': '-0.13', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/London'}},
    {'name': 'Rotterdam', 'params': {'latitude': '51.92', 'longitude': '4.48', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': 'Groningen', 'params': {'latitude': '53.22', 'longitude': '6.57', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': 'Berlin', 'params': {'latitude': '52.52', 'longitude': '13.41', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': 'Kraków', 'params': {'latitude': '50.06', 'longitude': '19.94', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': 'Prague', 'params': {'latitude': '50.09', 'longitude': '14.42', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
]


def text_by_wmo(code):
    for wmo in wmo_to_text:
        if code in wmo[0]:
            return wmo[1]


def get_forecast(params: dict):
    """Get meteo gorecast from Open Meteo for today"""
    url = 'https://api.open-meteo.com/v1/forecast/'
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        return r.status_code


def forecast_text():
    text = ''
    for place in places:
        fc = get_forecast(place.get('params'))['daily']
        text += f"{place.get('name')} H:{round(fc['temperature_2m_max'][0])}° L:{round(fc['temperature_2m_min'][0])}°" \
                f" {text_by_wmo(fc['weathercode'][0])}."

    messages = [
        {'role': 'system', 'content': 'Your a weather reporter and comedian. '
                                      'Highlight cities by country emoji and format title on separated line. '
                                      'Highlight weather condition by emoji. '
                                      'Make joke about every city forecast.'},
        {'role': 'user', 'content': f'Forecast data: {text}'},
    ]

    generated_text = generate_response(messages)
    translated_text = translate_text(generated_text)
    return translated_text
