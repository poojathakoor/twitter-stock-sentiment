import re
import string
import json
import pickle
from feature_extract import FeatureFinder
from classifier import Classifier
import pymongo

mongo = pymongo.Connection('localhost', 27017)

def classifyIt(tweets_collection):
    f = FeatureFinder()
    c = Classifier()
    unique_tweets = set([]); 
    tweets = db[tweets_collection].find()
    for tweet in tweets:
        if tweet['lang']=='en':
            text = tweet['text'].strip('\n')
            processed_tweet = f.processTweet(text)
            #remove duplicate tweets
            if processed_tweet not in unique_tweets:
                unique_tweets.add(processed_tweet)
                featureVector = f.getFeatureVector(processed_tweet)
                dbtweet = {}
                temp1 = {}
                dbtweet['_id'] = tweet['timestamp_ms']
                dbtweet['created_at'] = tweet['created_at']
                dbtweet['user'] = tweet['user']['screen_name']
                dbtweet['text'] = text
                temp1['sentiment'] = c.classifyNB(featureVector)
                dbtweet['NaiveBayes']= temp1
                temp2 = {}
                temp2['sentiment'] = c.classifyMaxEnt(featureVector)
                dbtweet['MaxEntropy'] = temp2
                temp3 = {}
                temp3['sentiment'] = c.classifySVM(featureVector)
                dbtweet['SVM'] = temp3
                json_tweet = json.dumps(dbtweet)
                json_tweet = json.loads(json_tweet)
                tweets_sentiment_db = mongo['Sentiment'+tweets_collection.split("_")[0]]
                collection = tweets_sentiment_db[tweets_collection]
                collection.save(json_tweet)
    print('   Done processing '+tweets_collection)
                
                                
if __name__ == "__main__":

    dbs = ['StreamFB', 'StreamAAPL']
    for dbname in dbs:
        print('Processing Database '+dbname+'...')
        db = mongo[dbname]
        collections = db.collection_names()
        for collection in collections:
            if(collection == 'system.indexes'):
                continue
            classifyIt(collection)
        print('success\n')
#end
  
    
  
        
