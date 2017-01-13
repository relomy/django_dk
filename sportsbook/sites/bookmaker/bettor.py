"""
COOKIES

ASP.NET_SessionId: caqeiqbsrzfuzud5kbpnwyj2
LandingPreference: Home
LanguagePreference: en-US
Name: ShowInfo
TimeZonePreference: 0
UserLoggedIn: true
_ga: GA1.2.1393353516.1484177531
_omappvp: true
_omappvs: true
_vwo_uuid_v2: B73D3D27F5D74E77E2F0E3BA0EFF2BD0|c95d937a82d2b823582df998492428e3
affid: INTERNET
affidSource: DefaultWebConfig
lb_height: 1118
om-202245: true
om-success-202245: true
om-success-cookie: true
passinfo:
reminfo:
usrinfo:
"""

import requests

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/55.0.2883.95 Safari/537.36')

def bet(game_id, prop_id, position, amount, **kwargs):
    """
    Response:
        Success:
        {
            "d": {
                "__type": "NGW.WebClient.AjaxMessages.PostBetsResp",
                "res": 0,
                "html": "..."
            }
        }
        Failure:
        {
            "d": {
                "__type": "NGW.WebClient.AjaxMessages.PostBetsResp",
                "res": 1,
                "errMsg": "Bet is not in the bet slip"
            }
        }
    """
    def add_to_bet_slip():
        cookies = {
            'affid': 'INTERNET',
            'affidSource': 'DefaultWebConfig',
            'ASP.NET_SessionId': os.environ['BOOKMAKER_SESSION_ID'],
            '_gat': '1',
            '_ga': 'GA1.2.1393353516.1484177531',
            '_vwo_uuid_v2': ('B73D3D27F5D74E77E2F0E3BA0EFF2BD0'
                             '|c95d937a82d2b823582df998492428e3'),
            'lang': 'en-US/',
            'tz': 'Pacific Standard Time',
            'selectedGame': game_id,
            'betTypeId': 'undefined',
        }
        headers = {
            'Pragma': 'no-cache',
            'Origin': 'https://livebetting.bookmaker.eu',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://livebetting.bookmaker.eu/ngwbet.aspx',
        }
        results = requests.post(
            'https://livebetting.bookmaker.eu/ngwbet.aspx/betSlipAdd',
            headers=headers,
            cookies=cookies,
            json={
                'propID': prop_id,
                'pos': position,
                'odds': kwargs['odds'],
                'points': 0
            })
        try:
            # Check particular formatting for a successful bet
            if 'errMsg' in results.json()['d']:
                print results.json()['d']['errMsg']
            return results.json()['d']['res'] == 0
        except (ValueError, KeyError):
            return False

    def place_bet():
        cookies = {
            'affid': 'INTERNET',
            'affidSource': 'DefaultWebConfig',
            'ASP.NET_SessionId': os.environ['BOOKMAKER_SESSION_ID'],
            '_ga': 'GA1.2.1393353516.1484177531',
            '_vwo_uuid_v2': 'B73D3D27F5D74E77E2F0E3BA0EFF2BD0|c95d937a82d2b823582df998492428e3',
            'lang': 'en-US/',
            'tz': 'Pacific Standard Time',
            'selectedGame': '84617',
            'betTypeId': 'undefined',
        }
        headers = {
            'Pragma': 'no-cache',
            'Origin': 'https://livebetting.bookmaker.eu',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://livebetting.bookmaker.eu/ngwbet.aspx',
        }
        results = requests.post(
            'https://livebetting.bookmaker.eu/ngwbet.aspx/betSlipPostOne',
            headers=headers,
            cookies=cookies,
            json={
                'propID': prop_id,
                'pos': position,
                'betAmt': amount,
                'lcopt': 1
            })
        try:
            # Check particular formatting for a successful bet
            if 'errMsg' in results.json()['d']:
                print results.json()['d']['errMsg']
            return results.json()['d']['res'] == 0
        except (ValueError, KeyError):
            return False

    if add_to_bet_slip():
        if place_bet():
            return True
        else:
            print '[ERROR/bookmaker.bettor] Unable to place bet.'
            return False
    else:
        print '[ERROR/bookmaker.bettor] Unable to add bet to bet slip.'
        return Fals
