import os
import datetime as dt

import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def war_chart():
    url = 'https://russianwarship.rip/api/v2/statistics'
    now = dt.datetime.now()
    date_from = now - dt.timedelta(days=7)

    r = requests.get(url, params={'date_from': date_from.strftime("%Y-%m-%d"), 'date_to': now.strftime("%Y-%m-%d")})
    stats = r.json()['data']['records']
    x = [record['date'] for record in stats]
    x = [dt.datetime.strptime(date, '%Y-%m-%d') for date in x]
    y = [record['increase']['personnel_units'] for record in stats]

    img = plt.imread(os.path.join(ROOT_DIR, 'static/zal.jpg'))
    fig, ax = plt.subplots()
    fig.figimage(img, 0, 0, alpha=0.6, resize=True)
    ax.bar(x, y, color='red')

    date_format = mdates.DateFormatter('%b %d')
    ax.xaxis.set_major_formatter(date_format)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))

    ax.set_ylabel('Втрати')
    ax.set_title('Тиждень росіян')

    tmp_dir = os.path.join(ROOT_DIR, 'tmp')
    plt.savefig(tmp_dir + '/war_chart.png')
    plt.close()


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