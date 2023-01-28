import requests


def get_war_stats():
    """Get latest war stats"""
    url = 'https://russianwarship.rip/api/v1/statistics/latest'
    r = requests.get(url)
    if r.status_code == 200:
        stats = r.json()['data']
        stats_total = stats['stats']
        stats_inc = stats['increase']
        return (
            f"{stats['day']}й день війни.\n"
            f"За вчора повиздихало {stats_inc['personnel_units']} русні, заголом було вбито {stats_total['personnel_units']} 🐷🐶\n"
            # f"танків: +{stats_inc['tanks']} ББМ: +{stats_inc['armoured_fighting_vehicles']} арта: +{stats_inc['artillery_systems']}"
            # f"{stats_inc['mlrs']} {stats_inc['aa_warfare_systems']} {stats_inc['planes']}"
            # f"{stats_inc['helicopters']} {stats_inc['vehicles_fuel_tanks']} {stats_inc['warships_cutters']}"
            # f"{stats_inc['cruise_missiles']} {stats_inc['uav_systems']} {stats_inc['special_military_equip']}"
            # f"{stats_inc['atgm_srbm_systems']}"
        )
    else:
        return f'Нема інфи по русні - {r.status_code}'