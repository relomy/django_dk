import os
import requests

def post_opp_to_slack(text):
    if text:
        response = requests.post(os.environ['SLACK_WEBHOOK_OPP_URL'],
                                 json={ 'text': text })
        if response.status_code != 200:
            print ('[ERROR/webhooks.post_opp_to_slack]: Unable to connect to'
                   ' Slack. %s' % response.text)

def post_bet_to_slack(text):
    if text:
        response = requests.post(os.environ['SLACK_WEBHOOK_BET_URL'],
                                 json={ 'text': text })
        if response.status_code != 200:
            print ('[ERROR/webhooks.post_bet_to_slack]: Unable to connect to'
                   ' Slack. %s' % response.text)
