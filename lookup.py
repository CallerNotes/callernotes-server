import requests

import ConfigParser, os

config = ConfigParser.ConfigParser()
config.read(['callernotes.cfg', os.path.expanduser('~/.callernotes.cfg')])

def twilio_nextcaller(number):
    username = config.get('twilio', 'username')
    password = config.get('twilio', 'password')

    url = "https://lookups.twilio.com/v1/PhoneNumbers/" + number + "/?AddOns=nextcaller_advanced_caller_id"

    headers = {
        'accept': "application/json",
        'content-type': "application/json"
    }

    response = requests.get(url, headers=headers, auth=(username, password))

    record = response.json()['add_ons']['results']['nextcaller_advanced_caller_id']['result']['records'][0]

    return record
