import os

import requests
# import datetime
# import matplotlib.pyplot as plt

# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#
# def war_chart():
#     url = 'https://russianwarship.rip/api/v2/statistics'
#     now = datetime.datetime.now()
#     month_ago = now - datetime.timedelta(days=30)
#
#     r = requests.get(url, params={'date_from': month_ago.strftime("%Y-%m-%d"), 'date_to': now.strftime("%Y-%m-%d")})
#     stats = r.json()['data']['records']
#     x = [record['date'] for record in stats]
#     y = [record['increase']['personnel_units'] for record in stats]
#
#     fig, ax = plt.subplots()
#     ax.plot(x, y)
#     ax.set_xlabel('Час')
#     ax.set_ylabel('Росіяни')
#     ax.set_title('Війна')
#
#     tmp_dir = os.path.join(ROOT_DIR, 'tmp')
#     plt.savefig(tmp_dir + '/war_chart.png')
#     plt.close()

def get_war_stats():
    """Get latest war stats"""
    url = 'https://russianwarship.rip/api/v1/statistics/latest'
    r = requests.get(url)
    if r.status_code == 200:
        stats = r.json()['data']
        stats_total = stats['stats']
        stats_inc = stats['increase']
        return (
            f"{stats['day']} день війни.\n"
            f"{stats_total['personnel_units']} (+{stats_inc['personnel_units']}) мертвих росіян."
        )
    else:
        return f'Нема інфи по русні - {r.status_code}'