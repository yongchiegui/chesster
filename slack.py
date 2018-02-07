import json
from slackclient import SlackClient

with open('config.json', 'r') as f:
    config = json.load(f)

CHESSTER_TOKEN = config['CHESSTER']['TOKEN']

slack_client = SlackClient(CHESSTER_TOKEN)

def connect():
    if slack_client.rtm_connect():
        return True


def write(text, channel):
    slack_client.api_call("chat.postMessage", channel=channel, text=text, as_user=True)


def read():
    return slack_client.rtm_read()


def get_name_from_id(id):
    id = id.lstrip('<@').rstrip('>').upper()
    api_call = slack_client.api_call("users.list")

    if api_call.get('ok'):
        users = api_call['members']
        for user in users:
            if user['id'] == id:
                return user['name']
    return None


def get_id_from_name(name):
    api_call = slack_client.api_call("users.list")

    if api_call.get('ok'):
        users = api_call['members']
        for user in users:
            if user['name'] == name:
                return user['id']
    return None
