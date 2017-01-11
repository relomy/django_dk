import os
import requests

def post_to_slack(text):
    response = requests.post(os.environ['SLACK_WEBHOOK_URL'],
                             json={ 'text': text })
    if response.status_code != 200:
        print ('[ERROR/webhooks.post_to_slack]: Unable to connect to Slack. %s'
               % response.text)
