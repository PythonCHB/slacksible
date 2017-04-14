from slackclient import SlackClient
import logging



'''
TODOS:
    * create logs:
        1. Debug log. slacksible_debug.log (10)
        2. stderr log. slacksible_stderr.log (40)
'''

def main():

    # TODO: change token to non-test token.non-test
    # TODO: move token out of file and have it read from elsewhere or during app boot
    token = "xoxb-168937458193-LUpXIw4f9Mk97iD6E1vtTFEr"

    sc = SlackClient(token)

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