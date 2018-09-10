#!/usr/bin/env python
"""
This is Slackbot. Slackbot is a bot on Slack that enjoys long walks on the
beach and other wholesome human activities. Please treat Slackbot with the
kind of respect that only a bot on slack commands.
"""
import time
import re
from settings import SLACK_BOT_TOKEN, BOT_ID
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(SLACK_BOT_TOKEN)
# slackbot's user ID in Slack: value is assigned after the bot starts up
slackbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
# commands
PING_COMMAND = "ping"
EXIT_COMMAND = "exit"
QUIT_COMMAND = "quit"
HELP_COMMAND = "help"
HEY_JUDE_MORSE = ".... . -.-- .--- ..- -.. ."
HEY_JUDE_COMMAND = "hey jude"
# variables
exit_flag = False
start_time = time.time()


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot
        commands.
        If a bot command is found, this function returns a tuple of
        command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == BOT_ID:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (at the beginning) in message text and returns
        the user ID which was mentioned.
        If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username,
    # the second group contains the remaining message
    return ((matches.group(1), matches.group(2).strip())
            if matches else (None, None))


def handle_command(command, channel):
    """
        Executes bot command if the command is known.
        Sends message
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(
        HELP_COMMAND)
    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(HEY_JUDE_COMMAND):
        response = HEY_JUDE_MORSE
    if command.startswith(PING_COMMAND):
        response = "Uptime {}".format(time.time() - start_time)
    if command.startswith(EXIT_COMMAND) or command.startswith(QUIT_COMMAND):
        response = "Catch ya later, alligator"
        global exit_flag
        exit_flag = True
    if command.startswith(HELP_COMMAND):
        response = ("Here are some commands:"
                    "\n `{}` \n `{}` \n `{}` \n `{}` \n `{}` \n".format(
                        HEY_JUDE_COMMAND, PING_COMMAND, HELP_COMMAND,
                        EXIT_COMMAND, QUIT_COMMAND))

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def list_channels():
    """
    Hits the api for a list of channels, returns channels info if found.
    Returns None if not found.
    """
    channels_call = slack_client.api_call("channels.list")
    if channels_call.get("ok"):
        return channels_call["channels"]
    return None


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print "Starter Bot connected and running!"
        # Runs through available channels and sends message
        for c in list_channels():
            print c["name"], c["id"]
            slack_client.api_call("chat.postMessage",
                                  channel=c["id"], text="Hello World!")
        # Read bot's user ID by calling Web API method `auth.test`
        slackbot_id = slack_client.api_call("auth.test")["user_id"]
        while not exit_flag:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print "Connection failed. Exception traceback printed above."
