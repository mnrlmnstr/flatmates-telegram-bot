import requests

def get_war_stats():
    """Get latest war stats"""
    url = 'https://russianwarship.rip/api/v1/statistics/latest'
    r = requests.get(url)
    if r.status_code == 200:
        stats = r.json()['data']
        return (
            f"{stats['day']}й день війни.\n"
            f"За вчора повиздихало {stats['increase']['personnel_units']} русні, заголом було вбито {stats['stats']['personnel_units']} 🐷🐶"
        )
    else:
        return f'Нема інфи по русні - {r.status_code}'