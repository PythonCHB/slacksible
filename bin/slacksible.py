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

start_time = time.time()

'''
BIG TODOS:
* figure out ara bootstrap as it needs python 2.7.13 (ansible?)
* figure out docker build so that i have 2 different versions of python running w/virtualenv?
* go back and re-do bootstrapping work for all of applciation
* configure encryption/decryption for config file(maybe)
* setup project with setuptools
* restructure tool how chris setup Py300-Spring2017/Examples/mailroom
'''

def cli_parser(args):
    '''
    Parses all arguments passed on command line.
    Creates an argparse class instance from passed arguments.
    '''
    parser = argparse.ArgumentParser(description="slacksible: Remote Ansible execution with run reports by Ara.")
    parser.add_argument('--verbose', '-v', action='count', default=0,
    help='-v: print debug info to console.')
    parser.add_argument('--token', '-t', type=str, help="Slack Bot Token generated from Slack platform.")
    return parser.parse_args(args)

def get_runpath(filepath):
    runpath = os.path.split(os.path.abspath(os.path.dirname(filepath)))[0]
    return runpath

def build_bot_config(args, filename):
    '''
    Parses config file. Overwrites config file parameters from
    CLI arguments passed.
    '''
    runpath = get_runpath(filename)
    config_dir = runpath+"/configuration/"
    with open(config_dir+"config.yml", 'r') as file:
        config = yaml.load(file)

    # Creates the expected log directory if it doesn't exist no matter where the application is executed from.
    if config["log_dir_enable"] and config["log_dir"]:
        log_dir = config["log_dir"]
    else:
        log_dir = runpath+"/log/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Creates handles for log files. Also creates the files themselves if they do not exist.
    config["debug_log"] = setup_logger("slacksible_debug", log_dir+"slacksible_debug.log", level=logging.DEBUG)
    config["stderr_log"] = setup_logger("slacksible_stderr", log_dir+"slacksible_stderr.log", level=logging.ERROR)
    config["usage_log"] = setup_logger("slacksible_metrics", log_dir+"slacksible_metrics.log", level=logging.INFO)

    if args.verbose:
        config["verbose"] = args.verbose
    if config["verbose"]:
        config["debug_log"].debug("==================================================\n\n\n")

    if args.token:
        config["SLACKSIBLE_TOKEN"] = args.token
        if config["verbose"]: config["debug_log"].debug("Token provided via CLI.")
    elif os.environ.get('SLACKSIBLE_TOKEN'):
        config["SLACKSIBLE_TOKEN"] = os.environ.get('SLACKSIBLE_TOKEN')
        if config["verbose"]: config["debug_log"].debug("Token retrieved from environment variable")
    elif config["SLACKSIBLE_TOKEN"]:
        if config["verbose"]: config["debug_log"].debug("Token retrieved from config file")
    else:
        if config["verbose"]: config["debug_log"].debug("Token not provided")
        raise NameError("Token not provided")

    if config["verbose"]: config["debug_log"].debug(config)
    return config


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
    def __init__(self, *args, **kwargs):
        # TODO: update code to pull in items noted below from config file
        print("args:" , args)
        print("kwargs: ", kwargs)
        self.verbose = kwargs.get("verbose")
        self.debug_log = kwargs.get("debug_log")
        self.stderr_log = kwargs.get("stderr_log")
        self.usage_log = kwargs.get("usage_log")
        self.sqlite_db = kwargs.get("ara_db")
        self.token = kwargs.get("SLACKSIBLE_TOKEN")
        self.bot_name = kwargs.get("bot_name")
        self.sc = SlackClient(self.token)


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
            pass
        else:
            if len(slack_data[0]["text"].split()) == 2 and slack_data[0]["text"].split()[1] == "ping":
                self.respond("Pong! :pingpong:", slack_data[0]["channel"])

            elif len(slack_data[0]["text"].split()) == 2 and slack_data[0]["text"].split()[1] == "help":
                self.respond('''
    ```
Commands:
    ara - show latest ansible runs
    ansilbe - send action to ansible (in progress)
    uptime - show bot uptime
    debug [on/off] - toggle debug logging on/off
    ping - bot respond with simple pong
    help - show this text``` ''', slack_data[0]["channel"])
                pass
            elif len(slack_data[0]["text"].split()) == 2 and slack_data[0]["text"].split()[1] == "seppuku":
                if self.verbose: self.debug_log.debug("Invoking seppuku function")
                self.seppuku(slack_data)

            elif len(text.split()) == 2 and text.split()[1] == "uptime":
                self.respond("--- %s Minutes ---" % ((time.time() - start_time) / 60), slack_data[0]["channel"])

            elif len(text.split()) == 3 and text.split()[1] == "debug":
                if self.verbose: self.debug_log.debug("Invoking toggle_debug function")
                self.toggle_debug(slack_data)

            elif len(text.split()) == 3 and text.split()[1] == "ara":
                if self.verbose: self.debug_log.debug("Invoking query_ARA function")
                self.query_ARA(slack_data)

            elif len(text.split()) == 3 and text.split()[1] == "ansible":
                if self.verbose: self.debug_log.debug("Sending action to Ansible")
                self.command_ansible(slack_data)


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
            self.verbose = 0
            self.respond("Debug mode off")
            if self.verbose: self.debug_log.debug("Debug mode off")
        elif slack_data[0]["text"].split()[2] == "on":
            self.verbose = 1
            self.respond("Debug mode on")
            if self.verbose: self.debug_log.debug("Debug mode on")


    def query_ARA(self, slack_data):
        '''
        Query ARA database for information to report
        '''

        if slack_data[0]["text"].split()[2] == "status":
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


    def command_ansible(self, slack_data):
        '''
        Send command to ansible to execute
        '''
        # TODO:
        # if slack_data[0]["text"].split()[2] == "run":
        #     if self.verbose: self.debug_log.debug("Running test Ansible job")
        #     print("Right before subprocess is called")
        #     runpath = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0])))[0]
        #     stdoutdata = subprocess.getoutput("ansible-playbook -i "+runpath+"/tests/ansible_tests/hosts "+runpath+"/tests/ansible_tests/test_playbook.yml")
        #     print("stdoutdata: ", stdoutdata)
        #     print("Right after subprocess is called")
        pass

    def listen(self):
            '''
            Connect bot to slack api and listen to data stream it has access to
            '''
            threads = []
            self.bot_id = self.determine_bot_id()
            if self.sc.rtm_connect():
                if self.verbose: self.debug_log.debug("================= Begin Listening =================")
                while True:
                    slack_data = self.sc.rtm_read()
                    if slack_data != [] and "text" in slack_data[0] and "message" in slack_data[0]["type"]:
                        if self.verbose: self.debug_log.debug(slack_data)
                        self.invoke_response = ["<@"+self.bot_id+">", self.bot_name, "slacksible"]
                        if "text" in slack_data[0] and slack_data[0]["text"].startswith(tuple(self.invoke_response)) and len(slack_data[0]["text"].split()) > 1:
                            #self.process_response(slack_data) # TODO: multi-thread/async this blocking action.")
                            thread = threading.Thread(target=self.process_response(slack_data), args=())
                            if self.verbose: self.debug_log.debug(thread)
                            thread.start()
                            if self.verbose: self.debug_log.debug(thread)
                            threads.append(thread)
                            if self.verbose: self.debug_log.debug(threads)
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
    args = cli_parser(sys.argv[1:])
    config = build_bot_config(args, sys.argv[0])
    bot = Slacksible(**config)
    try:
        bot.listen()
    except KeyboardInterrupt:
        config["debug_log"].debug("Exiting via KeyboardInterrupt")


if __name__ == '__main__':
    main()