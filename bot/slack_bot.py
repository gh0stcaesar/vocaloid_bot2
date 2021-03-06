#!/usr/bin/env python

import os
import time
import random
from slackclient import SlackClient

from beepboop import resourcer
from beepboop import bot_manager

import urllib, json
import urlparse

#http://api.search.nicovideo.jp/api/v2/video/contents/search?q=VOCALOID&targets=tags&fields=title,tags&filters[viewCounter][gte]=1000000&filters[categoryTags][0]=VOCALOID&_sort=-viewCounter&_limit=100&_offset=0

#playlists
playlist = {}
playlist["orangestar"] = "PLOXWDQbF5nQtflxUaCjx8w4VhpzPEAwHA"
playlist["pinocchioP"]= "PLSf-HCzj7cOvFosWKZdPJBTXw9iBfBp95"
playlist["deco*27"] = "PL6c6sPNdnX_UjsnvrQ_fssRHcon05f0Xd"
playlist["nbuna"] = "PL1oNojz8YMGHI9HMU48hNI2uhWzGYIdqw"
playlist["40mp"] = "PLtJnHhA9MVicF2uRb7zfOqX34cBpCCdXE"
playlist["kemu"] = "PLcksgEAZas2S_CMR6dhSdR4UBRdM9HgOt&index=4"
#playlist["jin"] = "PL9C906E72BDEB7F13"  #unofficial
#playlist{"classics"] = 


BOT_ID = "U3NGTJX2P"

names = {}
names["orangestar"] = "orangestar"
names["pinocchioP"]= "pinocchioP"
names["deco*27"] = "deco*27"
names["nbuna"] = "nbuna"
names["40mp"] = "40mp"
names["kemu"] = "kemu"
names["ke-san"] = "kemu"
names["ke-sanb"] = "kemu"
#names["jin"] = "jin"

names["os"] = "orangestar"
names["deco"] = "deco*27"
names["pino"] = "pinocchioP"

# constants
AT_BOT = "<@" + BOT_ID + ">"
random_song = "song"

# instantiate Slack & Twilio clients
SLACK_TOKEN = os.getenv("SLACK_TOKEN", "")
slack_client = SlackClient(SLACK_TOKEN)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    if command.startswith("search "):
        search_str = command[7:] + " vocaloid"

        url = u'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&order=Relevance&q='+search_str+'&type=video&key=AIzaSyD7CsWp3uxChY6fpJzBf1fFlj4r7W6Wk9o'        
        inp = urllib.urlopen(url.encode("UTF-8"))
        resp = json.load(inp)
        inp.close()

        item = resp['items'][0]

        response = "https://www.youtube.com/watch?v=" +  item["id"]["videoId"]

    elif command in names.keys():
        inp = urllib.urlopen(r'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails%2Cstatus&maxResults=50&playlistId='+playlist[names[command]]+'&key=AIzaSyD7CsWp3uxChY6fpJzBf1fFlj4r7W6Wk9o')
        resp = json.load(inp)
        inp.close()


        items = resp['items']

        rnd =  random.randint(0,len(items))
        response = "https://www.youtube.com/watch?v=" +  items[rnd]["contentDetails"]["videoId"]



    elif command == random_song:
        biglist = []
        for list,addr in playlist.iteritems():
            inp = urllib.urlopen(r'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails%2Cstatus&maxResults=50&playlistId='+addr+'&key=AIzaSyD7CsWp3uxChY6fpJzBf1fFlj4r7W6Wk9o')
            resp = json.load(inp)
            inp.close()

            items = resp['items']

            for item in items:
                biglist.append(item["contentDetails"]["videoId"])

        rnd = random.randint(0,len(biglist))
        response = "https://www.youtube.com/watch?v=" +  biglist[rnd]

    else:
        response = "invalid command"
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)



def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


