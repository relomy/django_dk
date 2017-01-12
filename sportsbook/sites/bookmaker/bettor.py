import requests

URL = 'https://livebetting.bookmaker.eu/ngwbet.aspx/betSlipPostOne'

HEADERS = {
    'Pragma': 'no-cache',
    'Origin': 'https://livebetting.bookmaker.eu',
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
    'Referer': 'https://livebetting.bookmaker.eu/ngwbet.aspx',
}

def get_cookies(game_id):
    return {
        'affid': 'INTERNET',
        'affidSource': 'DefaultWebConfig',
        'ASP.NET_SessionId': 'yqu5welq0f1yhg05h2bmb2qn',
        '_ga': 'GA1.2.1393353516.1484177531',
        '_vwo_uuid_v2': ('B73D3D27F5D74E77E2F0E3BA0EFF2BD0'
                         '|c95d937a82d2b823582df998492428e3'),
        'lang': 'en-US/',
        'tz': 'Pacific Standard Time',
        'selectedGame': game_id,
        'betTypeId': 'undefined',
    }

def get_data(prop_id, position, amount):
    return {
        'propID': prop_id,
        'pos': position,
        'betAmt': amount,
        'lcopt': 0 # What is this?
    }

def bet(game_id, prop_id, position, amount):
    requests.post(URL, headers=HEADERS, cookies=COOKIES, json=DATA)
