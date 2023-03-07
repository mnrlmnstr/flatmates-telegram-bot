import requests

from bot.ai import generate_response
from bot.translate import translate_text

wmo_to_emoji = {
    0: '☀️',  # Clear sky
    1: '🌤️',  # Mainly clear
    2: '⛅',   # Partly cloudy
    3: '☁️',   # Overcast
    45: '🌫️',  # Fog and depositing rime fog
    48: '🌁',   # Fog and depositing rime fog
    51: '🌧️',  # Drizzle: Light
    53: '🌧️',  # Drizzle: Moderate
    55: '🌧️',  # Drizzle: Dense intensity
    56: '❄️',   # Freezing Drizzle: Light
    57: '❄️',   # Freezing Drizzle: Dense intensity
    61: '🌧️',  # Rain: Slight
    63: '🌧️',  # Rain: Moderate
    65: '🌧️',  # Rain: Heavy intensity
    66: '❄️',   # Freezing Rain: Light intensity
    67: '❄️',   # Freezing Rain: Heavy intensity
    71: '🌨️',  # Snow fall: Slight intensity
    73: '🌨️',  # Snow fall: Moderate intensity
    75: '🌨️',  # Snow fall: Heavy intensity
    77: '🌨️',  # Snow grains
    80: '🌧️',  # Rain showers: Slight intensity
    81: '🌧️',  # Rain showers: Moderate intensity
    82: '🌧️',  # Rain showers: Violent intensity
    85: '🌨️',  # Snow showers: Slight intensity
    86: '🌨️',  # Snow showers: Heavy intensity
    95: '⛈️',  # Thunderstorm: Slight or moderate
    96: '⛈️',  # Thunderstorm with slight hail
    99: '⛈️',  # Thunderstorm with heavy hail
}

places = [
    {'name': '🇺🇦 Київ             ', 'params': {'latitude': '50.45', 'longitude': '30.52', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇬🇧 Лондон       ', 'params': {'latitude': '51.51', 'longitude': '-0.13', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/London'}},
    {'name': '🇳🇱 Ротердам   ', 'params': {'latitude': '51.92', 'longitude': '4.48', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇳🇱 Гронінген   ', 'params': {'latitude': '53.22', 'longitude': '6.57', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇩🇪 Берлін         ', 'params': {'latitude': '52.52', 'longitude': '13.41', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇵🇱 Краків         ', 'params': {'latitude': '50.06', 'longitude': '19.94', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇨🇿 Прага          ', 'params': {'latitude': '50.09', 'longitude': '14.42', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
]


def get_forecast(params: dict):
    url = 'https://api.open-meteo.com/v1/forecast/'
    r = requests.get(url, params=params)
    return r.json() if r.status_code == 200 else r.status_code


def forecast_text():
    forecast = ''
    for place in places:
        fc = get_forecast(place.get('params'))['daily']
        forecast += f"{place.get('name')} {wmo_to_emoji[fc['weathercode'][0]]}   H:{round(fc['temperature_2m_max'][0])}° L:{round(fc['temperature_2m_min'][0])}° \n"
    return forecast
