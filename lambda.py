import json
import os
import boto3
import requests
import tweepy
import random

def get_authenticated_twitter_api():
    
    consumer_key    = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']
    access_token    = os.environ['ACCESS_TOKEN']
    access_secret   = os.environ['ACCESS_TOKEN_SECRET']
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    
    api = tweepy.API(auth)
    
    return api

# def generate_random_word():
#     s3 = boto3.resource('s3')

#     content_object = s3.Object('twitter-bucket-for-words', 'json/whatever.json')
#     file_content = content_object.get()['Body'].read().decode('utf-8')
#     json_content = json.loads(file_content)
    
#     offset = random.randint(0, len(json_content)) 
    
#     return json_content[offset]

def generate_trends():
	#Get WOEID for USA
	#https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place
	WOEID = 23424977

	#Using the twitter API, get the top 10 trending topics
	twitter = get_authenticated_twitter_api()

	#Using the get_place_trends method, get the top 10 trending topics
	trends = [ trend['name'] for trend in twitter.get_place_trends(WOEID)[0]['trends'] ]

	#Pick a random one
	offset = random.randint(0, len(trends))

	return trends[offset]

def generate_funny_tweet(word: str):
    
    openai_endpoint = 'https://api.openai.com/v1/completions'
    openai_token = os.environ['OPENAI_BEARER']

    openai_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_token}'
    }
    
    openai_payload = {
        'model': 'text-davinci-002',
        'prompt': f'Write a funny tweet about {word.lower()}',
        'temperature': 0.75,
        'max_tokens': 280 
    }
    
    res = requests.post(openai_endpoint, headers=openai_headers, json=openai_payload)
    
    return res.json()['choices'][0]['text']

def lambda_handler(event, context):
    
	trend     = generate_trends()
	twitter   = get_authenticated_twitter_api()
	funny_twt = generate_funny_tweet(trend)

	#if the word already had a hashtag, remove it
	if '#' in trend:	
		trend = trend.replace('#', '')

	#take the word and split it into a list of words
	trend = trend.split()

	#Join the words back together with a hashtag in front of each word
	hashtag = ' '.join([f' #{w}' for w in trend])

	funny_twt = funny_twt + hashtag 

	twitter.update_status(funny_twt)


	return {  #         <---- RETURN THIS RIGHT AWAY 
		'statusCode': 200,
		'body': json.dumps(f'Making a fire tweet about {trend}')
	}
