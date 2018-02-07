from command import CommandManager
import json
import slack
import time

with open('config.json', 'r') as f:
    config = json.load(f)

CHESSTER_ID = config['CHESSTER']['ID']
SLEEP_SECONDS = config['GENERAL']['SLEEP_SECONDS']

command_queue = CommandManager()


def start_chesster():
    """Start up chesster"""
    if slack.connect():
        print 'Chesster is up and running!'
        run_chesster()


def run_chesster():
    """Let chesster listen for any commands and act on them"""
    while True:
        command, channel = get_command_from_chat(slack.read())
        if command is not None:
            command_queue.put_command_in_queue(command)

        response = command_queue.execute_top_command_in_queue()
        answer_in_chat(response, channel)
        time.sleep(SLEEP_SECONDS)


def get_command_from_chat(slack_output):
    """Retrieve any commands there are for chesster"""
    for output in slack_output:
        command = {}
        if 'text' in output and CHESSTER_ID in output['text']:
            command['user'] = output['user']
            command['text'] = output['text'].replace('<@' + CHESSTER_ID + '>', '').lower().split()
            channel = output['channel']
            return command, channel

    return None, None


def answer_in_chat(response, channel):
    """Chesster responds"""
    slack.write(response, channel)