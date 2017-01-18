import re
import requests
import os
from bs4 import BeautifulSoup
from celery import shared_task

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/55.0.2883.95 Safari/537.36')

def get_user(user_number=0):
    try:
        return {
            'username': os.environ['BETONLINE_USERNAME_%d' % user_number],
            'password': os.environ['BETONLINE_PASSWORD_%d' % user_number]
        }
    except KeyError:
        return None

def get_session_headers():
    """
    Currently unused.

    Args:
        None
    Returns:
        [tuple]: (ASP.NET_SessionId, BIGipServerBETONLINE.AG), E.g.:
                 ('gyzlofy2w3xd5lfhheiqkj55', '3825339402.20480.0000')
    """
    headers = {
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': USER_AGENT,
        'Accept': ('text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/webp,*/*;q=0.8'),
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    }
    response = requests.get('https://www.betonline.ag/come-back-soon',
                            headers=headers)
    try:
        session_id = re.findall(u'ASP.NET_SessionId=(.+?);',
                                response.headers['set-cookie'])
        ip_server = re.findall(u'BIGipServerBETONLINE.AG=(.+?);',
                               response.headers['set-cookie'])
        return ((session_id[0], ip_server[0])
                if session_id and len(session_id) == 1
                and ip_server and len(ip_server) == 1
                else None)
    except KeyError:
        return None

def get_login_token():
    return

@shared_task
def login(username, password, delay=1):
    cookies = {
        'ASP.NET_SessionId': os.environ['BETONLINE_SESSION_ID'],
        'AsiSystem': 'CurrentID=-1&CurrentUserName=',
        'KW_Search': 'domain=&kw=&HTTP_Refer=',
        'BIGipServerBETONLINE.AG': '3959557130.20480.0000',
        'CT_ProductType': 'sports',
        '__utmt': '1',
        '_gat_UA-30537011-1': '1',
        '_gat_UA-88758458-1': '1',
        '_ga': 'GA1.2.574533016.1484354896',
        '__utma': '203177346.574533016.1484354896.1484716108.1484778647.20',
        '__utmb': '203177346.6.10.1484778647',
        '__utmc': '203177346',
        '__utmz': ('203177346.1484354896.1.1.utmcsr=(direct)|'
                   'utmccn=(direct)|utmcmd=(none)'),
    }

    headers = {
        'Pragma': 'no-cache',
        'Origin': 'https://www.betonline.ag',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': ('text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/webp,*/*;q=0.8'),
        'Cache-Control': 'no-cache',
        'Referer': 'https://www.betonline.ag/come-back-soon',
        'Connection': 'keep-alive',
    }

    data = {
      'CustomerID': username,
      'Password': password,
      'button-submit-login': 'Login',
      'RememberMe': 'false'
    }

    try:
        response = requests.post('https://www.betonline.ag/login',
                                 headers=headers, cookies=cookies, data=data)
        soup = BeautifulSoup(response.text, 'html5lib')
        user_ids = soup.find_all(class_='userIdent')
        if user_ids and username in user_ids[0].string:
            print ('Logged in %s (%s)'
                   % (user_ids[0].string, os.environ['BETONLINE_SESSION_ID']))
            return True
        else:
            return False
    except Exception as e:
        if delay < 1024:
            delay *= 2
            print ('[WARNING/user.login]: Failed to log in (%s), reconnecting'
                   'in %d.' % (e, delay))
            return login.apply_async(username, password, delay, countdown=delay)
        else:
            return

def login_by_user_number(user_number=0):
    user = get_user(user_number)
    if user:
        return login(user['username'], user['password'])

