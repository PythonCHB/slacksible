#! /Users/jhefner/python_dev/uw_python/project/bin/python

import os
import sys
import logging
from slackclient import SlackClient
import sqlite3
import argparse
import time
import threading
import yaml
import subprocess

# TODO: move token out to env var or file and loaded during app boot
# Example- export SLACKSIBLE_TOKEN=xoxb-168959872961-kLJ5BASBuyeItLgKzDVx5UTX

# Logging levels:
# CRITICAL    50
# ERROR       40
# WARNING     30
# INFO        20
# DEBUG       10


'''
BIG TODOS:

* create sqlite3 connection to current ara db ~/.ara/ansible.sqlite
* use it to do a `select * from playbooks` and get the data we want to show
* figure out ara bootstrap as it needs python 2.7.13
* figure out docker build so that i have 2 different versions of python running w/virtualenv?
* complete functions that call from db to show data and return it to slack
* go back and re-do bootstrapping work for all of applciation
* write config file and setup encryption for it
* get config file imported and in place of code that shows that data
* setup project with setuptools
* restructure tool how chris setup Py300-Spring2017/Examples/mailroom
'''




# Defining here in global context so we capture its actual start time the closest as we can.
start_time = time.time()

def cli_parser():
    '''
    Parses all arguments passed on command line.
    Creates an argparse class instance from passed arguments.
    '''
    parser = argparse.ArgumentParser(description="slacksible: Remote Ansible execution with run reports by Ara.")
    parser.add_argument('--verbose', '-v', action='count', default=0,
    help='-v: print debug info to console.')
    parser.add_argument('--token', '-t', type=str, help="Slack Bot Token generated from Slack platform.")
    return parser.parse_args()


def setup_logger(log_name, log_file, level=logging.INFO):
    '''
    Easily setup multiple log files and levels
    '''
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


class Slacksible():
    '''
    Ansible slack bot class
    '''
    def __init__(self, token, verbose, debug_log, stderr_log, usage_log, *args, **kwargs):
        # TODO: update code to pull in items noted below from config file
        print("kwargs: ", kwargs)
        print("verbose: ", verbose)
        self.verbose = verbose
        self.debug_log = debug_log
        self.stderr_log = stderr_log
        self.usage_log = usage_log
        self.sqlite_db = "/Users/jhefner/.ara/ansible.sqlite" #TODO: add directory to config file, make that configurable from bootstrapper

        if token: #TODO: add token to config file
            self.token = token
            debug_log.debug("Token provided via CLI.")
        elif os.environ.get('SLACKSIBLE_TOKEN'):
            self.token = os.environ.get('SLACKSIBLE_TOKEN')
            debug_log.debug("Token retrieved from environment variable")
        else:
            debug_log.debug("Token not provided")
            raise NameError("Token not provided")
        self.bot_name = "ansible_slack_bot" #TODO: add bot_name to config file
        self.sc = SlackClient(self.token)

    def api_test(self): # simple api test for bot, remove once app proven.
        '''
        Simple bot API test
        '''
        self.sc.api_call("chat.postMessage",
                        channel="#slack_bot",
                        text="Hello from Python! :tada:"
                        )

    def determine_bot_id(self):
        '''
        Determine slack bot's own user id
        '''
        user_list= self.sc.api_call("users.list")
        for user in user_list["members"]:
            if user["name"] == self.bot_name:
                if self.verbose: self.debug_log.debug("Bot Slack ID: "+user["id"])
                return user["id"]

    def process_response(self, slack_data):
        '''
        Process user input and route to correct function to deal with request
        '''
        # TODO: create command list and route these requests to different functions
        text = slack_data[0]["text"]
        request = slack_data[0]["text"].split()
        length_request = len(slack_data[0]["text"].split())
        if self.verbose: self.debug_log.debug(request)
        if self.verbose: self.debug_log.debug(length_request)
        if self.verbose: self.debug_log.debug("Response being processed...")
        # TODO: capture what was requested as a command into metrics log

        if slack_data[0]["user"] == self.bot_id:
            if self.verbose: self.debug_log.debug("Ignoring flexo's own response.")
        else:
            if len(slack_data[0]["text"].split()) == 2 and slack_data[0]["text"].split()[1] == "help":
                pass
                #TODO: make bot list available commands

            elif len(slack_data[0]["text"].split()) == 2 and slack_data[0]["text"].split()[1] == "seppuku":
                if self.verbose: self.debug_log.debug("Invoking seppuku function")
                self.seppuku(slack_data)

            elif len(text.split()) == 2 and text.split()[1] == "uptime":
                self.respond("--- %s Minutes ---" % ((time.time() - start_time) / 60), slack_data[0]["channel"])

            elif len(text.split()) == 3 and text.split()[1] == "debug":
                if self.verbose: self.debug_log.debug("Invoking toggle_debug function")
                self.toggle_debug(slack_data)

            elif len(text.split()) == 2 and text.split()[1] == "ara":
                if self.verbose: self.debug_log.debug("Invoking query_ARA function")
                self.query_ARA(slack_data)


            # elif len(text.split()) == 2 and text.split()[1] == "":
            #     pass

            # elif len(text.split()) == 2 and text.split()[1] == "":
            #     pass

            # elif len(text.split()) == 2 and text.split()[1] == "":
            #     pass

            # elif len(text.split()) == 2 and text.split()[1] == "":
            #     pass

            # elif len(text.split()) == 2 and text.split()[1] == "":
            #     pass



    def seppuku(self, slack_data):
        '''
        Restarts running bot application (.py) file
        '''
        if self.verbose: self.debug_log.debug("\n=================\n   Slacksible bot restarting. \n=================\n\n\n")
        self.respond("Slacksible is restarting.", slack_data[0]["channel"])
        os.execv(__file__, sys.argv)

    def toggle_debug(self, slack_data):
        '''
        Toggles debug logging on via Slack command
        '''
        if slack_data[0]["text"].split()[2] == "off":
            if self.verbose: self.debug_log.debug("Debug command already off, requesting to be turned off again.")
            self.verbose = 0
            if self.verbose: self.respond("Debug mode off")
            else: self.respond("Debug already off")
        elif slack_data[0]["text"].split()[2] == "on":
            self.verbose = 1 #TODO: restructure this to understand the original verbose setting when bot was initiated.
            if self.verbose: self.debug_log.debug("Debug command currently off, requesting to be turned on.")
        else:
            self.respond("I do not understand that command.", slack_data[0]["channel"])


    def query_ARA(self, slack_data):
        '''
        Query ARA database for information to report
        '''
        conn = sqlite3.connect(self.sqlite_db)
        c = conn.cursor()

        response = '''
        ```Playbook:      |      Start Time(UTC):      |      Status:
'''
        c.execute("select path, time_start, complete from playbooks order by time_start desc LIMIT 5") #TODO: allow this to be configurable but protect against injection
        for row in c.execute("select path, time_start, complete from playbooks order by time_start desc LIMIT 5"):
            print(row[0].split('/')[-1], type(row[0].split('/')[-1]))
            print(row[1], type(row[1]))
            print(row[2], type(row[2]))
            print()
            playbook = row[0].split('/')[-1]
            time = row[1]
            if row[2]:
                completed = "Complete"
            else:
                completed = "Incomplete"
            response += "{} | {} | {} \n".format(playbook.strip(),time.strip(),str(completed).strip())
        response +="```"
        if self.verbose: self.debug_log.debug(response)
        self.respond(response, slack_data[0]["channel"])


    def command_ansible(self):
        '''
        Send command to ansible to execute
        '''
        # TODO:
        pass

    def listen(self):
            '''
            Connect bot to slack api and listen to data stream it has access to
            '''
            self.bot_id = self.determine_bot_id()
            if self.sc.rtm_connect():
                if self.verbose: self.debug_log.debug("================= Begin Listening =================")
                while True:
                    slack_data = self.sc.rtm_read()
                    if slack_data != [] and "text" in slack_data[0] and "message" in slack_data[0]["type"]:
                        if self.verbose: self.debug_log.debug(slack_data)
                        self.invoke_response = ["<@"+self.bot_id+">", self.bot_name, "slacksible"]
                        if "text" in slack_data[0] and slack_data[0]["text"].startswith(tuple(self.invoke_response)) and len(slack_data[0]["text"].split()) > 1:
                            self.process_response(slack_data) # TODO: multi-thread/async this blocking action.")
            else:
                self.stderr_log.error("Connection failed to Slack")

    def respond(self, message, channel):
        self.sc.api_call("chat.postMessage",
                      username=self.bot_name,
                      as_user=True,
                      channel=channel,
                      text=message
                      )


def main():
    args = cli_parser()

    # Creates the expected log directory if it doesn't exist no matter where the application is executed from.
    log_dir = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))[0]+"/log/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Creates handles for log files. Also creates the files themselves if they do not exist.
    #TODO: allow for location of log_dir to be overwritten by config file
    debug_log = setup_logger("slacksible_debug", log_dir+"slacksible_debug.log", level=logging.DEBUG)
    stderr_log = setup_logger("slacksible_stderr", log_dir+"slacksible_stderr.log", level=logging.ERROR)
    usage_log = setup_logger("slacksible_metrics", log_dir+"slacksible_metrics.log", level=logging.INFO)

    # TODO: restructure inputs so config file provides most inputs here
    bot = Slacksible(args.token, args.verbose, debug_log, stderr_log, usage_log)

    try:
        bot.listen()
    except KeyboardInterrupt:
        debug_log.debug("Exiting via KeyboardInterrupt")


if __name__ == '__main__':
    main()