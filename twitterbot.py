# -*- coding: utf-8 -*-
import tweepy
import json

#Twitter credentials
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

j_data = json.loads(open('public_html/data.json').read())

river_level = str(j_data['currentHeight'])
water_temp = str(j_data['currentWater'])
air_temp = str(j_data['currentTemp'])

tweet_string = 'Current Conditions - River Level: {} ft. Water Temp: {}°F. Air Temp: {}°F'.format(river_level,water_temp,air_temp)

api.update_status(tweet_string)