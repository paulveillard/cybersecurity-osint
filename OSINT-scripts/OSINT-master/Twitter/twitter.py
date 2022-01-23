#!/usr/bin/env python3
# OSINT/Twitter/twitter.py

# twitter.py
# Specigy a target twitter account
# Determine the targets birthday, device they tweet from
# Search through targets Followers & Following account name and handle for a string


# Imports
import os
import re
import sys
import json
import twint
import signal
import tweepy
import requests
import argparse
import collections
from bs4 import BeautifulSoup
from collections import Counter


### Utility Functions ###

def ctrl_c(sig, frame):
    print("\n{} chose to quit via CTRL+C!".format(os.environ['USER']))
    sys.exit(0)

def directory_setup(username):
    if not os.path.isdir(username): 
        os.mkdir(username, mode=770)

### END Utility Functions ###


### Birthday Functions ###

def find_birthday(username):

    search_url = "https://twitter.com/search?f=tweets&vertical=default&q=birthday%20OR%20bday%20to%3A{}".format(username)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
    r = requests.get(search_url, headers={'User-Agent': user_agent})

    date_list = []
    tweet_list = []
    
    soup = BeautifulSoup(r.text, 'html.parser')

    dates = soup.findAll("a", {"class": "tweet-timestamp js-permalink js-nav js-tooltip"})
    tweets = soup.findAll("div", {"class": "js-tweet-text-container"})

    for title in dates:
        x = title.get("title")
        date_list.append(x.split('-')[1].strip())

    for tweet in tweets:
        x = tweet.find('p').getText()
        tweet_list.append(x)

    print("\nTweets to @{} containing 'birthday' or 'bday':\n".format(username))
    for date, tweet_text in zip(date_list, tweet_list):
        print("  {} : {}".format(date, tweet_text))

    print("\nTop Three Dates: \n")
    for date in collections.Counter(date_list).most_common(3):
        day = date[0].split(' ')[0]
        month = date[0].split(' ')[1]
        print("  {} {} ({})".format(month, day, date[1]))

    print()
    exit(0)

### END Birthday Functions ###


### Followers/ Following Functions ###

def following(c, username):
    c.Output = "{}/Following".format(username)
    twint.run.Following(c)


def followers(c, username):
    c.Output = "{}/Followers".format(username)
    twint.run.Followers(c)


def search(username, search_string, f):

    filepath = "{}/{}".format(username, f)
    print("\n{} Matches: ".format(f))
    with open(filepath) as fp:  
        for line in fp:
            fields = line.strip().split('|')
            names = "  Name:{}\n  Handle:{}\n".format(fields[1], fields[2])
            if re.search(search_string, names, re.IGNORECASE):
                print("{}".format(names))

### END Followers/ Following Functions ###


### Device Functions ###

def get_device(username):

    auth = tweepy.OAuthHandler(
        '', '')
    auth.set_access_token('',
                          '')

    device_regex = "(?<=>).*?(?=<)"
    results = []
    
    tweet_list = tweepy.API(auth).user_timeline(screen_name=username, count=100)

    for tweet in tweet_list:
        device = re.findall(device_regex, tweet._json['source'])
        for x in device:
            results.append(x)

    count=Counter(results)

    for device, count in count.most_common():
        print('{} : {}'.format(device, count))

### END Device Functions ###


def main():

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--target", action='store', dest='username', required=True,  
                        help="Targets Twitter username")
    parser.add_argument("-b","--birthday", action='store_true',
                        help="Try to determine targets birthday")
    parser.add_argument("-d","--device", action='store_true',
                        help="Show which devices target tweets from")
    parser.add_argument("-s", "--search", action='store', dest='search_string',  
                        help="Dump and search list of targtes Followers/ Following for name/ username")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, ctrl_c)
    
    username = args.username
    search_string = args.search_string
    

    if args.birthday:
        find_birthday(username)

    elif args.device:
        get_device(username)

    elif search_string is not None:
        
        c = twint.Config()
        c.Username = username
        c.User_full = True
        
        directory_setup(username)

        if not os.path.isfile("{}/Followers".format(username)) and not os.path.isfile("{}/Following".format(username)): 
            print("[INFO] Dumping list of {}'s followers and following. This will take some time".format(username))
            print("[INFO] This only happens once")
            following(c, username)
            followers(c, username)

        search(username, search_string, "Followers")
        search(username, search_string, "Following")
        
        exit(0)
    
    else:
        parser.print_help()


if __name__== "__main__":
    main()
