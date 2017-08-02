import re
import string
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import itertools
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

class FeatureFinder:
  def __init__(self):
    self.featureVector = []
    self.features = {}
  #end
  
  def extract_features(self , tweet, featureList):
    tweet_words = set(tweet)
    self.features = {}
    for word in featureList:
        self.features['contains(%s)' % word] = (word in tweet_words)
    return self.features
  #end

  def getBigrams(self):
    #A bigram  is every sequence of two adjacent elements in a string of tokens
    #find only featured bigrams using pmi test
    score_fn=BigramAssocMeasures.pmi
    n=100
    bigram_finder = BigramCollocationFinder.from_words(self.featureVector)
    bigrams = bigram_finder.nbest(score_fn, n)
    #featureVector = [ngram for ngram in itertools.chain(featureVector, bigrams)]
    featVector = []
    for ngram in itertools.chain(self.featureVector, bigrams):
        if(',' in str(ngram)):
            ngram =' '.join(ngram)
        featVector.append(ngram)

    return featVector
  #end   

  def replaceTwoOrMore(self ,s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
  #end

  def getFeatureVector(self ,tweet):
    self.featureVector = []
    p = PorterStemmer()
    operators1 = set(('lt','gt','F','etc','facebook','fb','apple','aapl','amp','inc','ltd','twitter','blackberry','twtr','bbry','microsoft','msft','yahoo','yhoo'))
    operators2 = set(('down', 'nor', 'not', 'above', 'very', 'before', 'up', 'after', 'again', 'too', 'few', 'over'))
    stopWords = set(stopwords.words('english')) | operators1 
    stopWords = stopWords - operators2
    #tokenize all words / split tweet into words
    for w in word_tokenize(tweet):
      w = self.replaceTwoOrMore(w)
      
	  #check if the word stats with an alphabet
      val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
	  
	  #ignore if it is a stop word
      if(w in stopWords or val is None):
        continue
      else:
        #perform stemming eg removing ing from the end of word
        w = p.stem(w)
        self.featureVector.append(w)
	
    self.featureVector = self.getBigrams()	
    return self.featureVector
  #end

  def replaceWords(self, tweet):
    f = open('data/replaceWord.txt')
    for l in f:
      s = l.split('*')
      tweet = re.sub(r"\b%s\b" % s[0] , s[1], tweet)
    return tweet
  #end 

  def processTweet(self , tweet):
    # process the tweets

    #Convert to lower case
    tweet = tweet.lower()
    #Remove www.* or https?://*
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))',' ',tweet)
    #Remove @username 
    tweet = re.sub('@[^\s]+',' ',tweet)
	#Remove $companytag 
    tweet = re.sub('\$[^\s]+',' ',tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #remove punctuation
    tweet = tweet.replace('\'','')
    tweet = re.sub('[%s]' % re.escape(string.punctuation), ' ', tweet) 
    #replace words like thats to that is, isnt to is not
    tweet = self.replaceWords(tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    return tweet
  #end

  def processReqFeatTweet(self, tweet):
    #Remove newlines
    tweet = tweet.strip('\n')
    #Remove www.* or https?://*
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|f.processReqFeatTweet(text))',' ',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    return tweet
  #end