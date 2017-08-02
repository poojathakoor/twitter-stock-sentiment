import re
import string
import json
import pickle
from feature_extract import FeatureFinder


class Classifier:
    def __init__(self):
        self.features = {}
    #end

    def extract_features(self, featureVector):
        #tweet_words = set(tweet)
        featureList = pickle.load(open('data/featureList.pickle','rb'))
        self.features = {}
        for word in featureVector:
            #word = str(word)
            self.features[word] = (word in featureList)
        return self.features
    #end

    def classifySVM(self, featureVector):
        SVMClassifier = pickle.load(open('data/trained_model_svm.pickle','rb'))
        #print(extract_features(featureVector))
        return SVMClassifier.classify(self.extract_features(featureVector))
    #end

    def classifyMaxEnt(self, featureVector):
        MaxEntClassifier = pickle.load(open('data/trained_model_maxentropy.pickle','rb'))
        #print(extract_features(featureVector))
        return MaxEntClassifier.classify(self.extract_features(featureVector))
    #end

    def classifyNB(self, featureVector):
        NBClassifier = pickle.load(open('data/trained_model_naivebayes.pickle','rb'))
        #print(extract_features(featureVector))
        return NBClassifier.classify(self.extract_features(featureVector))
    #end

  
        
