#! /Users/jhefner/python_dev/uw_python/project/bin/python

from slackclient import SlackClient
import os
import sys
# import logging

# TODOS:
#     * create logs:
#         1. Debug log. slacksible_debug.log (10)
#         2. stderr log. slacksible_stderr.log (40)
#         3. usage log. slacksible_metrics.log
#     * create slack bot class:
#         1. solve token issue (dont show it in code)

# TODO: change token to non-test token
# TODO: move token out to env var or file and loaded during app boot
#   Example: os.environ[" ENV VAR TOKEN ALREADY LOADED "]
token = "xoxb-168959872961-Clds2jLyYvCQY3syhyEUSjKs"
sc = SlackClient(token)



class slacksible():
    """
    Ansible slack bot class
    """
    def __init__(self, args, **kwargs):
        self.token = os.environ["slacksible_token"]

        # TODO: find a better way, this is ugly as hell
        #       this finds one directory up from where the script is being run in /bin
        self.log_path = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))[0]+"/logs"


    def setup_dirs(self):
        '''
        Creates directory structure for a working application environment
        No return, makes changes directly on the filesystem
        '''
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
            # add dir creation to debug log
        else:
            pass
            # TODO: note existence of already existing log dir to debug log.

    @staticmethod
    def seppuku():
        '''
        Restart application
        '''
        # TODO: note restarting of application in debug log
        os.execv(__file__, sys.argv)
        # TODO: app should restart and not get to next line. raise error if it does

    def bot_listen(self):
        '''
        Connect to slack api and listen to data stream it has access to
        '''
        if sc.rtm_connect():
            print("====================Listening====================") # move to debug log
            while True: # TODO: capture exit from this loop in debug log
                slack_data = sc.rtm_read() # TODO: multi-thread/async this blocking action.
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

    def bot_query_ARA(self):
        # TODO: create cli parser for reading existing runs
        pass

    def bot_query_ansible(self):
        # TODO:
        pass

    def collect_usage_metrics(self):
        # TODO: capture commands directed at bot and sort by order of usage.
        pass



# simple api test for bot
def test():
    sc.api_call(
    "chat.postMessage",
    channel="#slack_bot",
    text="Hello from Python! :tada:"
    )

def main():
    print(os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))[0]+"/logs")


if __name__ == '__main__':
    main()