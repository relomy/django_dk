import os
import requests

import datetime
from pytz import timezone

def post_opp_to_slack(text):
    if text:
        print ('[INFO/webhooks.post_bet_to_slack]: Posting to Slack: %s'
               % (text))
        now_str = (datetime.datetime.now(timezone('US/Pacific'))
                                    .strftime('%Y-%d-%m %H:%M:%S'))
        response = requests.post(os.environ['SLACK_WEBHOOK_OPP_URL'],
                                 json={
                                     'text': '%s\n%s' % (now_str, text)
                                 })
        if response.status_code != 200:
            print ('[ERROR/webhooks.post_opp_to_slack]: Unable to connect to'
                   ' Slack. %s' % response.text)

def post_bet_to_slack(text):
    if text:
        print ('[INFO/webhooks.post_bet_to_slack]: Posting to Slack: %s'
               % (text))
        now_str = (datetime.datetime.now(timezone('US/Pacific'))
                                    .strftime('%Y-%d-%m %H:%M:%S'))
        response = requests.post(os.environ['SLACK_WEBHOOK_BET_URL'],
                                 json={
                                     'text': '%s %s' % (now_str, text)
                                 })
        now = (datetime.datetime.now(timezone('US/Pacific'))
                                .strftime('%Y-%d-%m %H:%M:%S'))
        if response.status_code != 200:
            print ('[ERROR/webhooks.post_bet_to_slack]: Unable to connect to'
                   ' Slack. %s' % response.text)
