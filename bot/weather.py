import requests

wmo_to_text = [
    ([0],               '🌞 Чисте небо'),
    ([1, 2, 3],         '👻 Похмуро'),
    ([45, 48],          '😶‍🌫️ Туман'),
    ([51, 53, 55],      '🌧 Мряка'),
    ([56, 57],          '🥶 Крижана мряка'),
    ([61, 63, 65],      '☔️ Дощ'),
    ([66, 67],          '🥶 Крижаний дощ'),
    ([71, 73, 75, 77],  '☃️ Снігопад'),
    ([80, 81, 82],      '💧Злива'),
    ([85, 86],          '❄️Сильний сніг❄️'),
    ([95],              '🌩 Можливо гроза'),
    ([96, 99],          '⚡️ Гроза'),
]

places = [
    {'name': '🇺🇦Київ', 'params': {'latitude': '50.45', 'longitude': '30.52', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇬🇧Лондон', 'params': {'latitude': '51.51', 'longitude': '-0.13', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/London'}},
    {'name': '🇳🇱Ротердам', 'params': {'latitude': '51.92', 'longitude': '4.48', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇳🇱Гронінген', 'params': {'latitude': '53.22', 'longitude': '6.57', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇩🇪Берлін', 'params': {'latitude': '52.52', 'longitude': '13.41', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇵🇱Краків', 'params': {'latitude': '50.06', 'longitude': '19.94', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
    {'name': '🇨🇿Прага', 'params': {'latitude': '50.09', 'longitude': '14.42', 'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'], 'timezone': 'Europe/Berlin'}},
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
        text += f"{place.get('name')}\nH:{round(fc['temperature_2m_max'][0])}° L:{round(fc['temperature_2m_min'][0])}°\n{text_by_wmo(fc['weathercode'][0])}\n\n"
    return text
