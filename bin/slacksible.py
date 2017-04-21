#! /Users/jhefner/python_dev/uw_python/project/bin/python

import os
import sys
import logging


from slackclient import SlackClient
import argparse

# TODOS:
#   * create logs:
#       1. Debug log. slacksible_debug.log (10)
#       2. stderr log. slacksible_stderr.log (40)
#       3. usage log. slacksible_metrics.log
#   * create slack bot class:
#       1. solve token issue (dont show it in code)
#   * change token to non-test token
#   * move token out to env var or file and loaded during app boot
#       Example: `export SLACKSIBLE_TOKEN=xoxb-168959872961-Clds2jLyYvCQY3syhyEUSjKs

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

# TODO: review if this can be moved to its own module
def setup_logger(log_name, log_file, level=logging.INFO):
    """
    Easily setup multiple log files and levels
    """
    if not os.path.isfile(log_file):
        with open(log_file, 'a'):
            os.utime(log_file, None)

    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    formatter = logging.Formatter("%(asctime)s - [%(threadName)s] [%(levelname)s]  %(message)s")
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
    def __init__(self, token, *args, **kwargs):
        print("args: ", args)
        print("kwargs: ", kwargs)

        # TODO: find a better way, this is ugly as hell
        #       this finds one directory up from where the script is being run in /bin
        self.log_dir = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))[0]+"/log/"

        self.debug_log = setup_logger("slacksible_debug", self.log_dir+"slacksible_debug.log", level=logging.DEBUG)
        self.debug_log.addHandler(logging.StreamHandler(sys.stdout)) # default for StreamHandler is stderr but we just want to print to console
        self.stderr_log = setup_logger("slacksible_stderr", self.log_dir+"slacksible_stderr.log", level=logging.ERROR)
        self.usage_log = setup_logger("slacksible_metrics", self.log_dir+"slacksible_metrics.log", level=logging.INFO)

        if token:
            self.token = token
            self.debug_log.debug("Token provided on CLI.")
        else:
            self.token = os.environ.get('SLACKSIBLE_TOKEN')
            self.debug_log.debug("Token retrieved from environment variable")
        self.sc = SlackClient(self.token)

    # TODO: review if this can be moved to its own module
    def setup_filesystem_dirs(self):
        '''
        Creates directory structure for a working application environment
        No return, makes changes directly on the filesystem
        '''
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
            self.debug_log.debug("Directory created: ",self.log_path,)
        else:
            self.debug_log.debug("Directory exists: ",self.log_path)

    def bot_seppuku(self):
        '''
        Restarts running bot application (.py) file
        '''
        self.debug_log.debug("Slacksible bot restarting.")
        os.execv(__file__, sys.argv)

        # App should restart and not get to next line. raise error if it does
        # TODO: write raise statement to notify that bot did not restart
        self.stderr_log.error("Slacksible bot restart FAILED.")

    def bot_api_test(self): # simple api test for bot
        '''
        Simple bot API test
        '''
        self.sc.api_call(
        "chat.postMessage",
        channel="#slack_bot",
        text="Hello from Python! :tada:"
        )

    def bot_listen(self):
        '''
        Connect bot to slack api and listen to data stream it has access to
        '''
        if self.sc.rtm_connect():
            self.debug_log.debug("====================Listening====================") # move to debug log
            while True: # TODO: capture exit from this loop in debug log
                slack_data = self.sc.rtm_read() # TODO: multi-thread/async this blocking action.
                if slack_data != [] and "text" in slack_data[0]:

                    # move to debug log
                    if "message" in slack_data[0]["type"]:
                        self.debug_log.debug("--------------------------")
                        self.debug_log.debug(slack_data)
                        if "user" in slack_data[0]:
                            self.debug_log.debug("user is:", slack_data[0]["user"])
                        if "type" in slack_data[0]:
                            self.debug_log.debug("type is:", slack_data[0]["type"])
                        if "text" in slack_data[0]:
                            self.debug_log.debug("message is:", slack_data[0]["text"])
                        if "channel" in slack_data[0]:
                            self.debug_log.debug("channel is:", slack_data[0]["channel"])
        else:
            self.stderr_log.error("Connection failed to Slack")

    def query_ARA(self):
        # TODO: create cli parser for reading existing runs
        pass

    def query_ansible(self):
        # TODO:
        pass

    def collect_usage_metrics(self):
        # TODO: capture commands directed at bot and sort by order of usage.
        pass


def main():
    args = cli_parser()
    bot = slacksible(args.token)
    bot.bot_listen()


if __name__ == '__main__':
    main()