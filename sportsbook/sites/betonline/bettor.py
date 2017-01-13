"""
COOKIES

.ASPXAUTH: 647FC919CE0EA802F6094E1DE84DF841F3AC92C521F0BF5AA0A626F39DE00659F250
           B2B125D5C95B289500FCBC5346F254F27FFF6DC305A9682F049C414C4398F1D6641E
           3E854C7C53959690DB3B6E4F5CD4626D67D7662B6E3EF2DF240B5D2DE00A3D0C17CA
           AF7952A90A8781CF8218ADA6F154
ASP.NET_SessionId: yp2o0w55fkounkfsp3jxtf45
AsiSystem: CurrentID=-1&CurrentUserName=
BIGipServerBETONLINE.AG: 3825339402.20480.0000
CT_ProductType: sports
Conversion.GUIID: 1e3d412b-973c-492d-1541-201701110213550
KW_Search: domain=&kw=&HTTP_Refer=
SecurityKey: rnJtj7ZrpQiNB8Wbl3/91GP/GcsUId6EUEXbFVWitZs=
__utma: 203177346.1850710465.1484177532.1484247673.1484252374.8
__utmb: 203177346.6.10.1484252374
__utmc: 203177346
__utmz: 203177346.1484184230.3.2.utmcsr=betonline.ag|utmccn=(referral)
        |utmcmd=referral|utmcct=/come-back-soon
_ga: GA1.2.1850710465.1484177532
_gat_UA-30537011-1: 1
_gat_UA-88758458-1: 1
balance: 48.00
"""

import os
import requests
from sportsbook.sites.betonline.user import get_user

URL = 'https://dgslivebetting.betonline.ag/ngwbet.aspx/betSlipPostOne'

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/55.0.2883.95 Safari/537.36')

def bet(game_id, prop_id, position, amount, **kwargs):
    """
    Response: {
        "d": {
            "__type":"NGW.WebClient.AjaxMessages.PostBetsResp",
            "res":1,
            "errMsg":"Bet is not in the bet slip"
        }
    }
    """
    def add_to_bet_slip():
        cookies = {
            'ASP.NET_SessionId': os.environ['BETONLINE_SESSION_ID'],
            'tz': 'Eastern Standard Time',
            '__utma': '203177346.1850710465.1484177532.1484270477.1484278687.13',
            '__utmb': '203177346.1.10.1484278687',
            '__utmc': '203177346',
            '__utmz': ('203177346.1484184230.3.2.utmcsr=betonline.ag'
                       '|utmccn=(referral)|utmcmd=referral'
                       '|utmcct=/come-back-soon'),
            '_gat_UA-88758458-1': '1',
            '_gat_UA-30537011-1': '1',
            '_ga': 'GA1.2.1850710465.1484177532',
        }
        headers = {
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://dgslivebetting.betonline.ag',
            'Accept': '*/*',
            'User-Agent': USER_AGENT,
            'Referer': 'https://dgslivebetting.betonline.ag/ngwbet.aspx',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        results = requests.post(
            'https://dgslivebetting.betonline.ag/ngwbet.aspx/betSlipAdd',
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
            'ASP.NET_SessionId': os.environ['BETONLINE_SESSION_ID'],
            'tz': 'Eastern Standard Time',
            '__utma': '203177346.1850710465.1484177532.1484270477.1484278687.13',
            '__utmc': '203177346',
            '__utmz': ('203177346.1484184230.3.2.utmcsr=betonline.ag'
                       '|utmccn=(referral)|utmcmd=referral'
                       '|utmcct=/come-back-soon'),
            '_gat_UA-30537011-1': '1',
            '_gat_UA-88758458-1': '1',
            '_ga': 'GA1.2.1850710465.1484177532',
        }

        headers = {
            'Pragma': 'no-cache',
            'Origin': 'https://dgslivebetting.betonline.ag',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://dgslivebetting.betonline.ag/ngwbet.aspx',
        }
        results = requests.post(
            'https://dgslivebetting.betonline.ag/ngwbet.aspx/betSlipPostOne',
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
            print '[ERROR/betonline.bettor] Unable to place bet.'
            return False
    else:
        print '[ERROR/betonline.bettor] Unable to add bet to bet slip.'
        return False
