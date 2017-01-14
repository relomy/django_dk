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

import os
import requests

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/55.0.2883.95 Safari/537.36')

def add_bet(game_id, prop_id, position, amount, **kwargs):
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
    response = requests.post(
        'https://livebetting.bookmaker.eu/ngwbet.aspx/betSlipAdd',
        headers=headers,
        cookies=cookies,
        json={
            'propID': prop_id,
            'pos': position,
            'odds': kwargs['odds'],
            'points': 0
        }
    )
    try:
        #if 'frozen' in response.json()['d']['html'].lower():
        #    return {
        #        'success': False,
        #        'message': 'Bet is frozen'
        #    }
        # Check particular formatting for a successful bet
        message = (response.json()['d']['errMsg']
                   if 'errMsg' in response.json()['d'] else '')
        return {
            'success': response.json()['d']['res'] == 0,
            'message': message
        }
    except (ValueError, KeyError):
        return {
            'success': False,
            'message': 'Malformed response'
        }

def place_bet(game_id, prop_id, position, amount, **kwargs):
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
    response = requests.post(
        'https://livebetting.bookmaker.eu/ngwbet.aspx/betSlipPostOne',
        headers=headers,
        cookies=cookies,
        json={
            'propID': prop_id,
            'pos': position,
            'betAmt': amount,
            'lcopt': 1
        }
    )
    try:
        # Check particular formatting for a successful bet
        message = (response.json()['d']['errMsg']
                   if 'errMsg' in response.json()['d'] else '')
        return {
            'success': response.json()['d']['res'] == 0,
            'message': message
        }
    except (ValueError, KeyError):
        return {
            'success': False,
            'message': 'Malformed response'
        }

def remove_bet(game_id, prop_id, position, **kwargs):
    cookies = {
        'affid': 'INTERNET',
        'affidSource': 'DefaultWebConfig',
        'ASP.NET_SessionId': os.environ['BOOKMAKER_SESSION_ID'],
        '_ga': 'GA1.2.512430787.1484354923',
        '_vwo_uuid_v2': 'EDFE8CDF4E5686950EAE4584259A811A|759194bb852b9cc6eaca71d531c66833',
        'lang': 'en-US/',
        'tz': 'Pacific Standard Time',
        'selectedGame': '84771',
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
    response = requests.post(
        'https://livebetting.bookmaker.eu/ngwbet.aspx/betSlipRemove',
        headers=headers,
        cookies=cookies,
        json={ 'propID': prop_id, 'pos': position }
    )
    try:
        # Check particular formatting for a successful bet
        message = (response.json()['d']['errMsg']
                   if 'errMsg' in response.json()['d'] else '')
        return {
            'success': response.json()['d']['res'] == 0,
            'message': message
        }
    except (ValueError, KeyError):
        return {
            'success': False,
            'message': 'Malformed response'
        }

