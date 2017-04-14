#! /Users/jhefner/python_dev/uw_python/project/bin/python

from slackclient import SlackClient


# import logging




# TODOS:
#     * create logs:
#         1. Debug log. slacksible_debug.log (10)
#         2. stderr log. slacksible_stderr.log (40)


def test():
    sc.api_call(
    "chat.postMessage",
    channel="#slack_bot_bullshit",
    text="Hello from Python! :tada:"
    )

# TODO: change token to non-test token
# TODO: move token out to env var or file and loaded during app boot
#   Example: os.environ[" ENV VAR TOKEN ALREADY LOADED "]
token = "xoxb-168959872961-Clds2jLyYvCQY3syhyEUSjKs"
sc = SlackClient(token)


def main():
    # test()
    if sc.rtm_connect(): # TODO: multi-thread this blocking action.
        print("====================Listening====================") # move to debug log
        while True:
            slack_data = sc.rtm_read()
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

if __name__ == '__main__':
    main()