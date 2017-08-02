import random
import collections
from nltk import NaiveBayesClassifier as nbc
from nltk.classify.maxent import MaxentClassifier as mec
import nltk.classify
import pickle
import math
from nltk.metrics import precision
from nltk.metrics import recall
from nltk.metrics import f_measure
from sklearn.svm import LinearSVC
from nltk.classify.scikitlearn import SklearnClassifier

class PerformanceFinder:
    def __init__(self):
        self.train_set_size = 0
        self.test_set_size = 0 
        self.total_size = 0
        self.trainSet = []
        self.testSet = []
        self.featureList = []
    
    def findsets(self,classifier):
        refsets = collections.defaultdict(set)
        self.testSets = collections.defaultdict(set)
        
        for i, (feats, label) in enumerate(self.testSet):
            refsets[label].add(i)
            observed = classifier.classify(feats)
            self.testSets[observed].add(i)
        return refsets,self.testSets
            
    def findAccuracy(self,classifier):
        return nltk.classify.accuracy(classifier,self.testSet)
    
    def findPrecision(self,classifier):
        refsets,self.testSets = self.findsets(classifier)
        return precision(refsets['bullish'], self.testSets['bullish']),precision(refsets['bearish'], self.testSets['bearish']),precision(refsets['neutral'], self.testSets['neutral'])
    
    def findRecall(self,classifier):
        refsets,self.testSets = self.findsets(classifier)
        return recall(refsets['bullish'], self.testSets['bullish']),recall(refsets['bearish'], self.testSets['bearish']),recall(refsets['neutral'], self.testSets['neutral'])
    
    def findFMetric(self,classifier):
        refsets,self.testSets = self.findsets(classifier)
        return f_measure(refsets['bullish'], self.testSets['bullish']),f_measure(refsets['bearish'], self.testSets['bearish']),f_measure(refsets['neutral'], self.testSets['neutral'])
 
    def findNBPerformance(self):
        self.train_set_size, self.test_set_size, self.trainSet, self.testSet = self.findSet()
        classifier = nbc.train(self.trainSet)    
        bull_precision, bear_precision, neutral_precision = self.findPrecision(classifier)
        bull_recall, bear_recall, neutral_recall = self.findRecall(classifier)
        bull_fmetric, bear_fmetric, neutral_fmetric = self.findFMetric(classifier)
        accuracy = self.findAccuracy(classifier)
        return self.train_set_size, self.test_set_size, accuracy, bull_precision, bear_precision, neutral_precision, bull_recall, bear_recall, neutral_recall, bull_fmetric, bear_fmetric, neutral_fmetric

    def findMEPerformance(self):
        self.train_set_size, self.test_set_size, self.trainSet, self.testSet = self.findSet()
        classifier = mec.train(self.trainSet,algorithm ='iis' ,max_iter=50) 
        bull_precision, bear_precision, neutral_precision = self.findPrecision(classifier)
        bull_recall, bear_recall, neutral_recall = self.findRecall(classifier)
        bull_fmetric, bear_fmetric, neutral_fmetric = self.findFMetric(classifier)
        accuracy = self.findAccuracy(classifier)
        return self.train_set_size, self.test_set_size, accuracy, bull_precision, bear_precision, neutral_precision, bull_recall, bear_recall, neutral_recall, bull_fmetric, bear_fmetric, neutral_fmetric

    def findSVMPerformance(self):
        self.train_set_size, self.test_set_size, self.trainSet, self.testSet = self.findSet()
        classifier = SklearnClassifier(LinearSVC())
        classifier.train(self.trainSet)  
        bull_precision, bear_precision, neutral_precision = self.findPrecision(classifier)
        bull_recall, bear_recall, neutral_recall = self.findRecall(classifier)
        bull_fmetric, bear_fmetric, neutral_fmetric = self.findFMetric(classifier)
        accuracy = self.findAccuracy(classifier)
        return self.train_set_size, self.test_set_size, accuracy, bull_precision, bear_precision, neutral_precision, bull_recall, bear_recall, neutral_recall, bull_fmetric, bear_fmetric, neutral_fmetric

    def findSet(self):
        featuresets = pickle.load(open('data/featureSets.pickle','rb'))
        random.shuffle(featuresets)
        self.total_size = len(featuresets)
        self.train_set_size = math.floor((3/4)*self.total_size)
        self.test_set_size = self.total_size - self.train_set_size
        train_set, test_set = featuresets[self.train_set_size:], featuresets[:self.test_set_size]
        self.featureList = []
        self.trainSet = []
        for line in train_set:
            featureVector = line[0]
            sentiment = line[1]
            self.trainSet.append((dict([(word, True) for word in featureVector]), sentiment))
            self.featureList = self.featureList + featureVector
        
        self.testSet = []
        for line in test_set:
            featureVector = line[0]
            sentiment = line[1]
            self.testSet.append((dict([(word, (word in self.featureList)) for word in featureVector]), sentiment))
    
    
        return self.train_set_size, self.test_set_size, self.trainSet, self.testSet
    
