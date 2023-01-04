import requests

wmo_to_text = [
    ([0],               '🌞 Чисте небо'),
    ([1, 2, 3],         '👻 Переважно ясно, похмуро'),
    ([45, 48],          '😶‍🌫️ Туман'),
    ([51, 53, 55],      '🌧 Мряка'),
    ([56, 57],          '🥶 Крижана мряка'),
    ([61, 63, 65],      '☔️ Дощ'),
    ([66, 67],          '🥶 Крижаний дощ'),
    ([71, 73, 75, 77],  '☃️ Снігопад'),
    ([80, 81, 82],      '💧Злива💧'),
    ([85, 86],          '❄️Сильний сніг❄️'),
    ([95],              '🌩 Можливо гроза'),
    ([96, 99],          '⚡️ Гроза'),
]

def text_by_wmo(code):
    for wmo in wmo_to_text:
        if code in wmo[0]:
            return wmo[1]

def get_forecast():
    """Get meteo gorecast from Open Meteo for today"""
    url = 'https://api.open-meteo.com/v1/forecast/'
    params = {
        'latitude': '50.45',
        'longitude': '30.52',
        'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'],
        'timezone': 'Europe/Berlin'
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        fc = r.json()['daily']
        return f"{text_by_wmo(fc['weathercode'][0])}\nH:{round(fc['temperature_2m_max'][0])}° L:{round(fc['temperature_2m_min'][0])}°"    
    else:
        return f'No weather data\n{r.status_code}{r.text}'