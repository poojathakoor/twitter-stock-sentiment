'''
This python file stores necessary tweet attributes to twitterData/ file 
and original tweet in json format to twitterData/native/ file
'''

#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import yahoo_stock
import datetime
import time
import json
import os,sys
import pymongo

#change the keyword to fetch stock tweets of choice e.g $AAPL , $TWTR 
keyword = '$AAPL'
       
#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    def __init__(self):
        self.no_of_tweets = 0
        self.keyword = keyword
        mongo = pymongo.Connection('localhost', 27017)
        db = mongo['Stream'+keyword.strip('$')]
        currDate = datetime.datetime.now()
        currDate = currDate.strftime("%d_%m_%Y")
        self.collection = db[keyword.strip('$')+'_'+str(currDate)]
     
    def on_data(self, data):
        tweet = json.loads(data)
        self.collection.save(tweet)
        self.no_of_tweets = self.no_of_tweets + 1
        print('success')
        return True

    def on_error(self, status):
        print ('Error :(')
        print (status)
        print ('No of tweets fetched :',self.no_of_tweets)

class TweetCollector:
    def __init__(self):
        self.keyword = keyword
        
    def parse_config(self):
      config = {}
      # from file args
      if os.path.exists('data/config.json'):
          with open('data/config.json') as f:
              config.update(json.load(f))
      # should have something now
      return config
	  
    def collect(self):  
        config = self.parse_config()
        print('\nConnecting to Twitter API...') 
        #This handles Twitter authentication and the connection to Twitter Streaming API
        l = StdOutListener()
        auth = OAuthHandler(config.get('consumer_key'), config.get('consumer_secret'))
        auth.set_access_token(config.get('access_token'), config.get('access_token_secret'))
        stream = Stream(auth, l)
        print('success\n')
	
        print('Fetching tweets... \nPress Ctrl+C in order to stop execution \n')
        try:
            #This line filter Twitter Streams to capture data by the keyword: e.g. '$FB - cashtag for facebook stock'
            stream.filter(track=[self.keyword])
        except(KeyboardInterrupt):
            print ('tweets stored in database')
            print ('No of tweets fetched : ',l.no_of_tweets)
            os._exit(0)
	
if __name__ == '__main__':
    t = TweetCollector()
    while True:
        try:
            t.collect()
        except:
            time.sleep(100)
            continue        
#To run the program
#python retrieve_tweets.py
