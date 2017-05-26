import sys, os, re
from bot import PATTERN, FILENAME

links = set()

# Get rid of duplicates
with open(FILENAME) as f:
    for link in f:
        if re.findall(PATTERN, link):
            links.add(link)

# Open every link
for link in links:
    os.system("start " + link)
