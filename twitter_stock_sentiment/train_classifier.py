import re
import string
import pickle
from nltk import NaiveBayesClassifier as nbc
from nltk.classify.maxent import MaxentClassifier as mec
from feature_extract import FeatureFinder
from sklearn.svm import LinearSVC
from nltk.classify.scikitlearn import SklearnClassifier

class TrainClassifier:
    def __init__(self):
        self.labels = ['bullish', 'bearish', 'neutral']
        self.data = {}
        self.trainSet = []
        self.featureList = []
        self.featuresets = []
    
    def train_classifier(self,featureVector):

        print('Training the Naive Bayes Classifier..')
        nbclassifier = nbc.train(featureVector)
        print('success\n')
        nbclassifier.show_most_informative_features(20)
        print('Storing the classfier object...')
        pickle.dump(nbclassifier, open('data/trained_model_naivebayes.pickle','wb'))
        print('success')
        print('-------------------------\n')
        
        print('Training the Maximum Entropy Classifier..')	
        meclassifier = mec.train(featureVector)
        print('success\n')
        meclassifier.show_most_informative_features()
        print('Storing the classfier object...')
        pickle.dump(meclassifier, open('data/trained_model_maxentropy.pickle','wb'))
        print('success')
        print('-------------------------\n')
                
        print('Training the SVM Classifier..')
        svmclassifier = SklearnClassifier(LinearSVC())
        svmclassifier.train(featureVector)
        print('success\n')
        print('Storing the classfier object...')
        pickle.dump(svmclassifier, open('data/trained_model_svm.pickle','wb'))
        print('success')
        print('-------------------------\n')
    #end

    def perform_feature_extraction(self, data):
        #category = bull/bear/neutral
        #docs = bull doc, bear doc, neutral doc
        self.trainSet = []
        self.featureList = []
        self.featuresets = []
        f = FeatureFinder()
        print('extracting features...')
        for sentiment, docs in data.items():
            for tweet in docs:
                processedTweet = f.processTweet(tweet)
                featureVector = f.getFeatureVector(processedTweet)
                self.featuresets.append((featureVector,sentiment))
                self.featureList = self.featureList + featureVector
                self.trainSet.append((dict([(word, True) for word in featureVector]), sentiment))
        print('success\n')
        # Remove featureList duplicates
        self.featureList = list(set(self.featureList))
        print('storing featurelist and featureVector')
        pickle.dump( self.featureList, open( "data/featureList.pickle", "wb" ) )
        pickle.dump( self.featuresets, open( "data/featuresets.pickle", "wb" ) )
        print('success\n')
  
        return self.trainSet
    #end

    def read_in_data(self):
        self.data = {}
        for label in self.labels:
            f = open('training_data/'+label+'.txt','r')
            self.data[label] = f.readlines()
            f.close

        return self.data
    #end
  
if __name__ == "__main__":
  #dictionary tweets and label
  tc = TrainClassifier()
  data = tc.read_in_data() 
  featureVector = tc.perform_feature_extraction(data)
  tc.train_classifier(featureVector)
  
#end
  