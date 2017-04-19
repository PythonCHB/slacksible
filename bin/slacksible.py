#! /Users/jhefner/python_dev/uw_python/project/bin/python

import os
import sys
import logging


from slackclient import SlackClient
import argparse

# TODOS:
#     * create logs:
#         1. Debug log. slacksible_debug.log (10)
#         2. stderr log. slacksible_stderr.log (40)
#         3. usage log. slacksible_metrics.log
#     * create slack bot class:
#         1. solve token issue (dont show it in code)

# TODO: change token to non-test token

# TODO: move token out to env var or file and loaded during app boot
#   Example: `export SLACKSIBLE_TOKEN=xoxb-168959872961-Clds2jLyYvCQY3syhyEUSjKs`

# sc = SlackClient(token)

def cli_parser():
    """
    Parses all arguments passed on command line.
    Creates an argparse class instance from passed arguments.
    """
    parser = argparse.ArgumentParser(description="slacksible: Remote Ansible execution with run reports by Ara.")
    parser.add_argument('--verbose', '-v', action='count', default=0,
    help='-v: print debug info to console.')
    parser.add_argument('--token', '-t', required=True, type=str, help="Slack Bot Token generated from Slack platform.")
    return parser.parse_args()


class slacksible():
    """
    Ansible slack bot class
    """
    def __init__(self, token, *args, **kwargs):
        print("args: ", args)
        print("kwargs: ", kwargs)

        # TODO: find a better way, this is ugly as hell
        #       this finds one directory up from where the script is being run in /bin
        self.log_dir = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))[0]+"/logs"
        self.debug_log = logging.getLogger("slacksible_debug")
        self.stderr_log = logging.getLogger("slacksible_stderr")
        self.usage_log = logging.getLogger("slacksible_metrics")

        if token:
            self.token = token
            self.debug_log.debug("Token provided on CLI.")
        else:
            self.token = os.environ.get('SLACKSIBLE_TOKEN')
            self.debug_log.debug("Token retrieved from environment variable")
        self.sc = SlackClient(self.token)


    def setup_filesystem_dirs(self):
        '''
        Creates directory structure for a working application environment
        No return, makes changes directly on the filesystem
        '''
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
            self.debug_log.debug("Directory created: ",self.log_path,)
        else:
            pass
            # TODO: note existence of already existing log dir to debug log.

    @staticmethod
    def bot_seppuku():
        '''
        Restarts running bot application (.py) file
        '''
        # TODO: note restarting of application in debug log
        os.execv(__file__, sys.argv)
        # TODO: app should restart and not get to next line. raise error if it does

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
            print("====================Listening====================") # move to debug log
            while True: # TODO: capture exit from this loop in debug log
                slack_data = self.sc.rtm_read() # TODO: multi-thread/async this blocking action.
                if slack_data != [] and "text" in slack_data[0]:

                    # move to debug log
                    if "message" in slack_data[0]["type"]:
                        print("--------------------------")
                        print(slack_data)
                        if "user" in slack_data[0]:
                            print("user is:", slack_data[0]["user"])
                        if "type" in slack_data[0]:
                            print("type is:", slack_data[0]["type"])
                        if "text" in slack_data[0]:
                            print("message is:", slack_data[0]["text"])
                        if "channel" in slack_data[0]:
                            print("channel is:", slack_data[0]["channel"])
        else:
            print("Connection failed to Slack") # move to error log

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