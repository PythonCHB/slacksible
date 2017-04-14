from slackclient import SlackClient
import logging

logging.getLogger("slacksible_stderr").setLevel(logging.
logging.basicConfig(filename='slacksible_stderr.log',
                    filemode='a',
                    format

def main():
