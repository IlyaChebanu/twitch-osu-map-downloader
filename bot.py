import socket
import sys, os
import re


PATTERN = re.compile(r"\bhttps:\/\/osu\.ppy\.sh\/\w\/\d{1,10}\b")
FILENAME = "maps.txt"

# will be changed to command line arguments in a later version
NICK = "downloadbot"
PASS = "" # oauth key


class Downloader_IRC:
    def __init__(self, username, passwd):
        self.username = username
        self.auth = passwd
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect(("irc.chat.twitch.tv", 6667))


    def get_message(self):
        text = self.irc.recv(2040).decode("utf-8").strip()
        # program can't encode emoji back to utf-8, so if one occurs, ignore it
        try:
            if text.find('PING') != -1:
                self.irc.send(("PONG " + text.split()[1] + '\r\n').encode("utf-8"))
            return text
        except UnicodeEncodeError:
            return ""

    def parse_links(self):
        msg = self.get_message()
        links = re.findall(PATTERN, msg)

        if os.path.exists(FILENAME):
            flag = "a"
        else:
            flag = "w"

        with open(FILENAME, flag) as f:
            for link in links:
                f.write(link + "\n")

    def run(self, channel):
        self.irc.send("PASS {}\r\n".format(self.auth).encode("utf-8"))
        self.irc.send("NICK {}\r\n".format(self.username).encode("utf-8"))
        self.irc.send("JOIN #{}\r\n".format(channel).encode("utf-8"))

        text = self.irc.recv(2040).decode("utf-8")

        if "NOTICE" in text:
            print("Failed to connect, exiting.")
            quit()

        print("Successfully connected to {}'s stream".format(channel))
        while True:
            self.parse_links()



if __name__ == '__main__':
    # start the IRC bot
    irc = Downloader_IRC(NICK, PASS)
    irc.run(sys.argv[1])
