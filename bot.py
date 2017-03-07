import socket
import sys
import urllib.request


# will be changed to command line arguments in a later version
PASS = "oauth:your-key-goes-here"
NICK = "your-name-goes-here"
CHANNEL = "miruhong"


'''
* find_next_alpha(string)
returns index offset in the substring where the first alphabetical character
occurs. if one is not found, string must have ended so return last index..
really bad way of doing it due to hardcoded offsets in the link parser, may
fix in a later version.
'''
def find_next_alpha(s):
    i_off = 0
    for c in s:
        if c.isalpha():
            return i_off
        i_off += 1
    return len(s) + 1



class Downloader_IRC:
    def __init__(self, username, passwd):
        self.username = username
        self.auth = passwd
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect(("irc.chat.twitch.tv", 6667))
        # in python 3 strings sent over sockets must be encoded and decoded
        # failed authentification will be dealth with in a later version
        self.irc.send("PASS {}\r\n".format(passwd).encode("utf-8"))
        self.irc.send("NICK {}\r\n".format(username).encode("utf-8"))

    def get_message(self):
        text = self.irc.recv(2040).decode("utf-8").strip()
        # program can't encode emoji back to utf-8, so if one occurs, ignore it
        try:
            # if a PING message is received, send PONG back to not get timed out
            if text.find('PING') != -1:
                self.irc.send(("PONG " + text.split()[1] + '\r\n').encode("utf-8"))
            return text
        except UnicodeEncodeError:
            return ""

    def parse_link(self, msg):
        index = msg.find("https://osu.ppy.sh")
        if index != -1: # if the index is found
            # 21 - hardcoded offset to the beginning of map ID
            end_index = find_next_alpha(msg[index + 21:])
            # if the next character after song ID is "&" then return None
            # since we want to skip it (ID differs for difficulties)
            # in a later version this will be dealt with differently and instead
            # original ID will be parsed from page source

            # since we're trying to access an index that may not exist, we
            # want to ignore that case
            try:
                if msg[index + 20 + end_index] == "&":
                    return None, None
            except:
                pass
            # because of the way find_next_alpha is set up, end_index is either
            # end of ID or end of line, hence except can be left empty
            map_id = msg[index + 21:index + 20 + end_index]
            # return the map download link
            return "https://osu.ppy.sh/d/" + map_id + "/", map_id
        # if the index wasn't found, return none
        return None, None

    def download_map(self):
        link, map_id = self.parse_link(self.get_message())
        if link:
            urllib.request.urlretrieve(link, map_id + ".osz")
            return map_id # later will be used for unzipping and halding dupes

    def run(self, channel):
        # join the desired channel and start listening for maps
        self.irc.send("JOIN #{}\r\n".format(channel).encode("utf-8"))
        text = self.irc.recv(2040).decode("utf-8")
        print(text)
        while 1:
            self.download_map()


# start the IRC bot
irc = Downloader_IRC(NICK, PASS)
irc.run(CHANNEL)
