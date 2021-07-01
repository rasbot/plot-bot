#! /usr/bin/python3

import json
import time
import os
import re
import argparse
import string
import tweepy
import numpy as np

from datetime import datetime, timedelta, timezone
from pytz import timezone
import pytz

hashtags = ['AI', 'bot', 'AIgenerated', 'AIbot', 'plotbot',
            'movieplot', 'ML', 'neuralnet', 'machinelearning', 'deeplearning']


def seconds_until_datetime(date_time):
    """Gives the seconds from the current time until a specified datetime

       args: 
           date_time (str): a datetime string suchas '2020-04-03 23:59:59'
       returns:
           diff_in_seconds (int): an integer representing the time in seconds
               from the current time (when the function is executed) to the 
               datetime string passed as a parameter.
    """
    target_time = datetime.strptime(date_time.split(' ')[0] + ' ' + str(int(date_time.split(' ')[1].split(
        ':')[0])) + ':' + date_time.split(':')[1] + ':' + date_time.split(':')[2]+'.0', '%Y-%m-%d %H:%M:%S.%f')
    utc_dt = pytz.utc.localize(datetime.utcnow())
    pst_tz = timezone('US/Pacific')
    pst_dt = pst_tz.normalize(utc_dt.astimezone(pst_tz))
    ct = pst_dt.strftime('%Y-%m-%d %H:%M:%S')
    current_time = datetime.strptime(ct.split(' ')[0] + ' ' + str(int(ct.split(' ')[1].split(
        ':')[0])) + ':' + ct.split(':')[1] + ':' + ct.split(':')[2]+'.0', '%Y-%m-%d %H:%M:%S.%f')
    diff_string = str(target_time-current_time)
    if len(diff_string.split(',')) > 1:
        substring_day_to_seconds = int(
            diff_string.split(',')[0].split(' ')[0])*86400
        substring_hour_to_seconds = int(diff_string.split(
            ',')[1].split(':')[0].split(' ')[1])*3600
        substring_minutes_to_seconds = int(
            diff_string.split(',')[1].split(':')[1].split(':')[0])*60
        substring_seconds = int(diff_string.split(',')[1].split(':')[2])
        diff_in_seconds = substring_day_to_seconds+substring_hour_to_seconds + \
            substring_minutes_to_seconds+substring_seconds  # compensate for UTC time
        return diff_in_seconds
    else:
        substring_hour_to_seconds = int(diff_string.split(':')[0])*3600
        substring_minutes_to_seconds = int(
            diff_string.split(':')[1].split(':')[0])*60
        substring_seconds = int(diff_string.split(':')[2])
        diff_in_seconds = substring_hour_to_seconds + \
            substring_minutes_to_seconds+substring_seconds
        return diff_in_seconds


def add_hashtags(plot, hashtags):
    np.random.shuffle(hashtags)
    tags = hashtags[:3]
    keep_looping = True
    i = 0
    while keep_looping:
        if len(plot) < 275:
            _plot = plot + ' #' + tags[i]
            if len(_plot) < 280:
                plot = _plot
        else:
            keep_looping = False
        if i <= 1:
            i += 1
        else:
            break
    return plot


def tweet(randomize=False, hashtags=False):
    with open("data/auth.json") as f:
        keys = json.load(f)
    f.close()

    # authentication of consumer key and secret
    auth = tweepy.OAuthHandler(keys["consumer_key"], keys["consumer_secret"])

    # authentication of access token and secret
    auth.set_access_token(keys["access_token"], keys["access_token_secret"])
    api = tweepy.API(auth)

    with open("plotbot.json") as f:
        data = json.load(f)

    if randomize:
        # key of the random entry
        plot_key = np.random.choice(list(data.keys()))
    else:
        plot_key = list(data.keys())[0]

    plot = data[plot_key]

    # delete plot from JSON file
    del data[plot_key]
    with open("plotbot.json", "w") as f:
        data = json.dump(data, f, indent=4, sort_keys=False)

    if hashtags:
        plot = add_hashtags(plot, hashtags)

    api.update_status(plot)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--randomize", type=bool, dest="randomize")
    parser.add_argument("--start_datetime", type=str, dest="start_datetime")

    args = parser.parse_args()

    if args.start_datetime:
        print('start datetime good')
        delay_time = seconds_until_datetime(args.start_datetime)
    else:
        delay_time = 0

    time.sleep(delay_time)

    while True:
        tweet()
        time.sleep(21600)

