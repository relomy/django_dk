import requests

URL = 'https://dgslivebetting.betonline.ag/ngwbet.aspx/betSlipPostOne'

HEADERS = {
    'Pragma': 'no-cache',
    'Origin': 'https://dgslivebetting.betonline.ag',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                   ' AppleWebKit/537.36 (KHTML, like Gecko)'
                   ' Chrome/55.0.2883.95 Safari/537.36'),
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': '*/*',
    'Cache-Control': 'no-cache',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://dgslivebetting.betonline.ag/ngwbet.aspx',
}

def get_cookies(game_id):
    return {
        'ASP.NET_SessionId': '3gsmy45n4sooatvoa1l3ymy2',
        'tz': 'Eastern Standard Time',
        '__utma': '203177346.1850710465.1484177532.1484196690.1484199248.5',
        '__utmc': '203177346',
        '__utmz': ('203177346.1484184230.3.2.utmcsr=betonline.ag'
                   '|utmccn=(referral)|utmcmd=referral|utmcct=/come-back-soon'),
        '_gat_UA-30537011-1': '1',
        '_ga': 'GA1.2.1850710465.1484177532',
        '_gat_UA-88758458-1': '1',
    }

def get_data(prop_id, position, amount):
    return {
        'propID': prop_id,
        'pos': position,
        'betAmt': amount,
        'lcopt': 1 # What is this?
    }

def bet(game_id, prop_id, position, amount):
    requests.post(URL, headers=HEADERS, cookies=COOKIES, json=DATA)
