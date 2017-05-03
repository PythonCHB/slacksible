#! /Users/jhefner/python_dev/uw_python/project/bin/python

import os
import sys
import logging

#just for debug printing, remove later
import json

from slackclient import SlackClient
import argparse

# TODO: move token out to env var or file and loaded during app boot
# Example- export SLACKSIBLE_TOKEN=xoxb-168959872961-kLJ5BASBuyeItLgKzDVx5UTX

# Logging levels:
# CRITICAL    50
# ERROR       40
# WARNING     30
# INFO        20
# DEBUG       10


def cli_parser():
    """
    Parses all arguments passed on command line.
    Creates an argparse class instance from passed arguments.
    """
    parser = argparse.ArgumentParser(description="slacksible: Remote Ansible execution with run reports by Ara.")
    parser.add_argument('--verbose', '-v', action='count', default=0,
    help='-v: print debug info to console.')
    parser.add_argument('--token', '-t', type=str, help="Slack Bot Token generated from Slack platform.")
    return parser.parse_args()


def setup_logger(log_name, log_file, level=logging.INFO):
    """
    Easily setup multiple log files and levels
    """
    if not os.path.isfile(log_file):
        with open(log_file, 'a'):
            os.utime(log_file, None)
    formatter = logging.Formatter("%(asctime)s - [%(module)s] [%(levelname)s]  %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


class slacksible():
    """
    Ansible slack bot class
    """
    def __init__(self, token, verbose, debug_log, stderr_log, usage_log, *args, **kwargs):
        print("kwargs: ", kwargs)
        print("verbose: ", verbose)
        self.verbose = verbose
        self.debug_log = debug_log
        self.stderr_log = stderr_log
        self.usage_log = usage_log

        # TODO: build config file to read token and bot_name
        if token:
            self.token = token
            debug_log.debug("Token provided via CLI.")
        elif os.environ.get('SLACKSIBLE_TOKEN'):
            self.token = os.environ.get('SLACKSIBLE_TOKEN')
            debug_log.debug("Token retrieved from environment variable")
        else:
            debug_log.debug("Token not provided")
            raise NameError("Token not provided")
        self.bot_name = "ansible_slack_bot"
        self.sc = SlackClient(self.token)


    def api_test(self): # simple api test for bot
        '''
        Simple bot API test
        '''
        self.sc.api_call(
        "chat.postMessage",
        channel="#slack_bot",
        text="Hello from Python! :tada:"
        )

    def determine_bot_id(self):
        user_list= self.sc.api_call("users.list")
        for user in user_list["members"]:
            if user["name"] == self.bot_name:
                self.debug_log.debug("Bot Slack ID: "+user["id"])
                return user["id"]

    def process_response(self, user, channel):
        '''
        Process user input and route to correct function to deal with request
        '''
        # TODO: create command list and route these requests to different functions
        pass

    def seppuku(self):
        '''
        Restarts running bot application (.py) file
        '''
        self.debug_log.debug("Slacksible bot restarting.")
        os.execv(__file__, sys.argv)

    def toggle_debug(self):
        '''
        Toggles debug logging on via Slack command
        '''
        pass

    def query_ARA(self):
        # TODO: create cli parser for reading existing runs
        pass

    def query_ansible(self):
        # TODO:
        pass

    def collect_usage_metrics(self):
        # TODO: capture commands directed at bot and sort by order of usage.
        pass

    def listen(self):
            '''
            Connect bot to slack api and listen to data stream it has access to
            '''
            self.bot_id = self.determine_bot_id()
            if self.sc.rtm_connect():
                self.debug_log.debug("================= Begin Listening =================")
                while True:
                    slack_data = self.sc.rtm_read()
                    if slack_data != [] and "text" in slack_data[0] and "message" in slack_data[0]["type"]:
                        # if "message" in slack_data[0]["type"]:
                        self.debug_log.debug(slack_data)
                        if "text" in slack_data[0] and slack_data[0]["text"].startswith("<@"+self.bot_id+">"):
                            self.process_response(slack_data[0]["user"], slack_data[0]["channel"]) # TODO: multi-thread/async this blocking action.")
            else:
                self.stderr_log.error("Connection failed to Slack")


def main():
    args = cli_parser()

    # TODO: find a better way, this is ugly as hell
    # this finds one directory up from where the script is being run in /bin and adds the log dir at the end
    log_dir = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))[0]+"/log/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # TODO: originally i thought i'd like different log files for each logging level,
    # similarly to how Unicorn works. now im unsure. may need to compress this to 1 file.
    debug_log = setup_logger("slacksible_debug", log_dir+"slacksible_debug.log", level=logging.DEBUG)
    stderr_log = setup_logger("slacksible_stderr", log_dir+"slacksible_stderr.log", level=logging.ERROR)
    usage_log = setup_logger("slacksible_metrics", log_dir+"slacksible_metrics.log", level=logging.INFO)

    # TODO: restructure inputs so the log files go in under the *args array
    bot = slacksible(args.token, args.verbose, debug_log, stderr_log, usage_log)
    try:
        bot.listen()
    except KeyboardInterrupt:
        debug_log.debug("Exiting via KeyboardInterrupt")


if __name__ == '__main__':
    main()