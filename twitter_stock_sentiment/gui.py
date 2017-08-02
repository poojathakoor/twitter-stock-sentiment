import tkinter as tk
import datetime
from yahoo_stock import YahooStock
from tkinter.ttk import *
from get_tweets import GetTweets
from classifier import Classifier
from feature_extract import FeatureFinder
from performance import PerformanceFinder
from datetime import timedelta
import threading
import pymongo
import os
#import classify


TITLE_FONT = ("Helvetica", 18, "bold")
CUSTOM_FONT = ("Calibri", 13)
CUSTOM_FONT2 = ("Calibri", 14, "bold")

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry("500x700+500+100")
        self.title("Stock Sentiment Classifier")
        self.resizable(0,0)
        self.style = tk.ttk.Style()
        self.style.theme_use("clam")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            frame = F(container, self)
            self.frames[F] = frame
            # put all of the pages in the same location; 
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, c):
        '''Show a frame for the given class'''
        frame = self.frames[c]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        
        
        '''
        label1 = tk.Label(self, text="First").grid(row=0)
        lable2 = tk.Label(self, text="Second").grid(row=1)
        '''
        button0 = Button(self, text="Sentiment Finder", 
                            command=lambda: controller.show_frame(StartPage)).grid(row=0,column=0)
        button1 = Button(self, text="Classifier Performance", 
                            command=lambda: controller.show_frame(PageOne)).grid(row=0,column=1)
        button2 = Button(self, text="Market Correlation",
                            command=lambda: controller.show_frame(PageTwo)).grid(row=0,column=2)
                            
        tk.Label(self, text="Choose Symbol: ").grid(row=2,column=0)
        
        self.var1 = tk.StringVar(self)
        self.var1.set("$FB") # initial value

        option1 = tk.OptionMenu(self, self.var1, "$AAPL", "$FB", "$TWTR", "$GOOG", "$MSFT","$BBRY", "$YHOO", "$ZNGA","$IBM" ,"$LNKD").grid(row=2,column=1,pady=2)
        
        tk.Label(self, text="Choose Classifier: ").grid(row=3,column=0,pady=2)
        
        self.var2 = tk.StringVar(self)
        self.var2.set("Naive Bayes") # initial value

        option2 = tk.OptionMenu(self, self.var2, "Maximum Entropy", "Naive Bayes","SVM").grid(row=3,column=1,pady=2)
        
        
        self.calculate = Button(self, text="Find Sentiment",command=self.performAction)
        
        self.calculate.grid(row=4,columnspan=3,pady=2)
        
    
        self.company = tk.StringVar()
        CompanyName = tk.Label(self, textvariable=self.company,font=TITLE_FONT).grid(row=5,columnspan=3)
        self.company.set("")
        
        self.date = tk.StringVar()
        dateL = tk.Label(self, textvariable=self.date, font=CUSTOM_FONT).grid(row=6,columnspan=3)
        self.date.set("")
        
        self.open = tk.StringVar()
        openL = tk.Label(self, textvariable=self.open).grid(row=7,column=0)
        self.open.set("")
        self.current = tk.StringVar()
        self.current.set("")
        currentL = tk.Label(self, textvariable=self.current).grid(row=7,column=1)
        self.change = tk.StringVar()
        self.change.set("")
        changeL = tk.Label(self, textvariable=self.change).grid(row=7,column=2)
        
        self.textbox = tk.Text(self,height='20',width='53',relief=tk.SUNKEN,font=CUSTOM_FONT, wrap=tk.WORD)
        self.textbox.grid(row=8,columnspan=3)
        scrl = tk.Scrollbar(self, command=self.textbox.yview)
        self.textbox.config(yscrollcommand=scrl.set)
        scrl.grid(row=8, column = 2,sticky='ens')
        
        
        quitButton = Button(self, text="Quit", command=self.quit).grid(row=9,column=2,pady=5)

    def performAction(self):
        thread = threading.Thread(target=self.performAct, name='Thread1')
        thread.start()
    
    def performAct(self):
        g = GetTweets()
        f = FeatureFinder()
        c = Classifier()
        y = YahooStock()
        unique_tweets = set([]); 
        symb = self.var1.get()
        tweets = g.getTwitterData(symb)
        classifier_name = self.var2.get()
        self.company.set(y.get_company_name(symb.strip('$')))
        #print(y.get_historical_prices(symb.strip('$'),'2015-03-12'))
        currDate = datetime.datetime.now()
        currDate = currDate.strftime("%a %b %d %Y")
        self.date.set(str(currDate))
        self.open.set('Open: $'+y.get_today_open(symb.strip('$')))
        self.current.set('Current: $'+y.get_price(symb.strip('$')))
        self.change.set('Change: '+y.get_change(symb.strip('$')))
        
        
        self.textbox.config(state=tk.NORMAL)
        self.textbox.delete(1.0,tk.END)
        for tweet in tweets:
            text = tweet['text']
            text = text.encode('ascii','ignore').decode('unicode_escape')
            processed_tweet = f.processTweet(text.strip('\n'))
            if processed_tweet not in unique_tweets:
                unique_tweets.add(processed_tweet)
                featureVector = f.getFeatureVector(processed_tweet)
                if(classifier_name == 'Maximum Entropy'):
                    sentiment = c.classifyMaxEnt(featureVector)
                elif(classifier_name == 'Naive Bayes'):
                    sentiment = c.classifyNB(featureVector)
                elif(classifier_name == 'SVM'):
                    sentiment = c.classifySVM(featureVector)
                
                user = tweet['user']
                time = tweet['created_at']
                #Mon Mar 09 13:40:43 +0000 2015
                time = datetime.datetime.strptime(time, '%a %b %d %X %z %Y') + timedelta(hours=+5, minutes=+30)
                time = time.strftime('%b %d %I:%M %p')
                
                self.textbox.insert(tk.INSERT,user)
                self.textbox.insert(tk.INSERT,'\t\t\t\t'+str(time)+'\n')
                
                #size = self.customFont['size']
                #self.customFont.configure(size=size-2)
                self.textbox.insert(tk.INSERT,f.processReqFeatTweet(text)+'   '+sentiment.upper()+'\n')
                self.textbox.insert(tk.INSERT,'-----------------------------------------------------------------------------------------------\n\n')
        self.textbox.config(state=tk.DISABLED)

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 

        button0 = Button(self, text="Sentiment Finder", 
                            command=lambda: controller.show_frame(StartPage)).grid(row=0,column=0)
        button1 = Button(self, text="Classifier Performance", 
                            command=lambda: controller.show_frame(PageOne)).grid(row=0,column=1)
        button2 = Button(self, text="Market Correlation",
                            command=lambda: controller.show_frame(PageTwo)).grid(row=0,column=2)
                            
        tk.Label(self, text="       Classifier performance evaluation      ", font=TITLE_FONT).grid(row=1,columnspan=3,pady=5)
        
        tk.Label(self, text="Choose Classifier: ").grid(row=2,column=0,pady=5)
        
        self.var1 = tk.StringVar(self)
        self.var1.set("Naive Bayes") # initial value

        option2 = tk.OptionMenu(self, self.var1,"Naive Bayes","Maximum Entropy","SVM").grid(row=2,column=1,pady=5)

        
        self.findAccButton =  Button(self, text="Find Performance",command=self.performAction)
        self.findAccButton.grid(row=3,columnspan=3,pady=2)
        
        self.accOutput = tk.PanedWindow(self,relief=tk.SUNKEN)
        self.prfOutput = tk.PanedWindow(self,relief=tk.SUNKEN)
        
        self.var2 = tk.StringVar(self)
        self.var3 = tk.StringVar(self)
        txt1 = Label(self.accOutput, textvariable=self.var2, font = CUSTOM_FONT2)
        txt2 = Label(self.prfOutput, textvariable=self.var3, font = CUSTOM_FONT2)
        self.var2.set("\n\n\n\n\n")
        self.var3.set("\n\n\n\n\n\n\n\n\n\n\n")
        self.accOutput.add(txt1)
        self.accOutput.grid(row=4,columnspan=3,sticky='ew',pady=10)
        self.prfOutput.add(txt2)
        self.prfOutput.grid(row=5,columnspan=3,sticky='ew',pady=10)
        
        quitButton = Button(self, text="Quit", command=self.quit).grid(row=6,column=2,pady=5)
        #self.updateDescription(self.var1.get())
    
    def performAction(self):
        thread = threading.Thread(target=self.performAct, name='Thread1')
        thread.start()
    
    def performAct(self):
        a = PerformanceFinder()
        classifier_name = self.var1.get()
        if classifier_name == 'Naive Bayes':
            train_set_size, test_set_size, accuracy, bull_precision, bear_precision, neutral_precision, bull_recall, bear_recall, neutral_recall, bull_fmetric, bear_fmetric, neutral_fmetric = a.findNBPerformance()
        elif classifier_name == 'Maximum Entropy':
            train_set_size, test_set_size, accuracy, bull_precision, bear_precision, neutral_precision, bull_recall, bear_recall, neutral_recall, bull_fmetric, bear_fmetric, neutral_fmetric = a.findMEPerformance()
        elif classifier_name == 'SVM':
            train_set_size, test_set_size, accuracy, bull_precision, bear_precision, neutral_precision, bull_recall, bear_recall, neutral_recall, bull_fmetric, bear_fmetric, neutral_fmetric = a.findSVMPerformance()
        accuracy = round(accuracy*(100),2)
        bull_precision = round(bull_precision*(100),2)
        bear_precision = round(bear_precision*(100),2)
        neutral_precision = round(neutral_precision*(100),2)
        bull_recall = round(bull_recall*(100),2)
        bear_recall = round(bear_recall*(100),2)
        neutral_recall = round(neutral_recall*(100),2)
        bull_fmetric = round(bull_fmetric*(100),2)
        bear_fmetric = round(bear_fmetric*(100),2)
        neutral_fmetric = round(neutral_fmetric*(100),2)
        self.var2.set("\tClassifier:\t\t\t"+classifier_name+"\n\tSize of Training Data:\t"+str(train_set_size)+"\n\tSize of Test Data:\t\t"+str(test_set_size)+"\n\tAccuracy:\t\t\t"+ str(accuracy)+"%")      
        self.var3.set("\tBullish Precision:\t\t"+str(bull_precision)+"%\n\tBullish Recall:\t\t"+str(bull_recall)+"%\n\tBullish F-Metric:\t\t"+str(bull_fmetric)+"%\n\n\tBearish Precision:\t\t"+str(bear_precision)+"%\n\tBearish Recall:\t\t"+str(bear_recall)+"%\n\tBearish F-Metric:\t\t"+str(bear_fmetric)+"%\n\n\tNeutral Precision:\t\t"+str(neutral_precision)+"%\n\tNeutral Recall:\t\t"+str(neutral_recall)+"%\n\tNeutral F-Metric:\t\t"+str(neutral_fmetric)+"%")
        
class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        button0 = Button(self, text="Sentiment Finder", 
                            command=lambda: controller.show_frame(StartPage)).grid(row=0,column=0)
        button1 = Button(self, text="Classifier Performance", 
                            command=lambda: controller.show_frame(PageOne)).grid(row=0,column=1)
        button2 = Button(self, text="Market Correlation",
                            command=lambda: controller.show_frame(PageTwo)).grid(row=0,column=2)
        
        tk.Label(self, text="                Sentiment And Stock                   ", font=TITLE_FONT).grid(row=1,columnspan=3,pady=5)
        
        tk.Label(self, text="Choose Symbol: ").grid(row=2,column=0)
        
        
        tk.Label(self, text="Choose Classifier: ").grid(row=2,column=0,pady=2)
        self.var2 = tk.StringVar(self)
        self.var2.set("Naive Bayes") # initial value

        option2 = tk.OptionMenu(self, self.var2, "Maximum Entropy", "Naive Bayes","SVM").grid(row=2,column=1,pady=2)
        
        tk.Label(self, text="Choose Symbol: ").grid(row=3,column=0,pady=2)
        self.var1 = tk.StringVar(self)
        self.var1.set("$AAPL") # initial value
        option1 = tk.OptionMenu(self, self.var1, "$AAPL", "$FB",command = self.update_menu).grid(row=3,column=1,pady=2)
        
        self.mongo = ''
        
        tk.Label(self, text="Choose Database: ").grid(row=4,column=0,pady=2)
        self.var3 = tk.StringVar(self)
        self.var3.set("Select") # initial value
        
        self.option3 = tk.OptionMenu(self,self.var3, "Select")
        self.menu = self.option3.children["menu"]
        self.option3.grid(row=4,column=1,pady=2)
        
        self.find = Button(self, text="Find",command=self.performAction).grid(row=5,column=1,pady=4)
        
        
        self.output = tk.PanedWindow(self,relief=tk.SUNKEN)
     
        
        self.var4 = tk.StringVar(self)
        txt1 = Label(self.output, textvariable=self.var4, font = CUSTOM_FONT2)
        
        self.var4.set("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        self.output.add(txt1)
        self.output.grid(row=6,columnspan=3,sticky='ew',pady=10)
        
        self.bull = Button(self,text = "Bullish Tweets",command=self.openFile1).grid(row=7,column=0,pady=2)
        self.bear = Button(self,text = "Bearish Tweets",command=self.openFile2).grid(row=7,column=1,pady=2)
        self.neutral = Button(self,text = "Neutral Tweets",command=self.openFile3).grid(row=7,column=2,pady=2)
        
        quitButton = Button(self, text="Quit", command=self.quit).grid(row=9,column=2,pady=5)
        self.lock = threading.Lock()
    
    def openFile1(self):
        os.startfile("data\\bull.txt")
        
    def openFile2(self):
        os.startfile("data\\bear.txt")
        
    def openFile3(self):
        os.startfile("data\\neutral.txt")
    
    def update_menu(self,*OPTIONS):
        self.mongo = pymongo.Connection('localhost', 27017)
        symb = self.var1.get()
        db = self.mongo['Sentiment' + symb.strip('$')]
        collections = db.collection_names()
        self.menu.delete(0, "end")
        self.OPTIONS = ["1"]
        for value in collections:
            if value != 'system.indexes':
                self.menu.add_command(label=value, command=lambda v=value: self.var3.set(v))
    
    def performAction(self):
        thread = threading.Thread(target=self.performAct, name='Thread1')
        thread.start()
        
    def performAct(self):
        with self.lock:
            file1 = open('data/bull.txt','w')
            file2 = open('data/bear.txt','w')
            file3 = open('data/neutral.txt','w')
            
        y = YahooStock()
        symb = self.var1.get()
        classifier_name = self.var2.get()
        collection = self.var3.get()
        map = {'Naive Bayes':'NaiveBayes','Maximum Entropy':'MaxEntropy','SVM':'SVM'}
        db = self.mongo['Sentiment' + symb.strip('$')]
        db2 = self.mongo['Stream' + symb.strip('$')]
        
        temp = collection.split('_')
        date = temp[3] + '-' +temp[2] + '-' +temp[1] 
        stock_data = y.get_historical_prices(symb.strip('$'), date, date)
        opn = stock_data[date]['Open']
        low = stock_data[date]['Low']
        high = stock_data[date]['High']
        close = stock_data[date]['Close']
        bull_count = db[collection].find({map[classifier_name]:{"sentiment":"bullish"}}).count()
        bear_count = db[collection].find({map[classifier_name]:{"sentiment":"bearish"}}).count()
        neutral_count = db[collection].find({map[classifier_name]:{"sentiment":"neutral"}}).count()
        tweet_count = db2[collection].find().count()
        self.var4.set('\tDate\t:  '+str(date)+'\n\tOpen\t:  $'+str(opn)+'\n\tLow\t:  $'+str(low)+'\n\tHigh\t:  $'+str(high)+'\n\tClose\t:  $'+str(close)+
        '\n\n\tMessage Volume\t:  '+str(tweet_count)+'\n\tBullish Count\t:  '+str(bull_count)+'\n\tBearish Count\t:  '+str(bear_count)+'\n\tNeutral Count\t:  '+str(neutral_count)+'\n\tBull-bear ratio\t:  '+str(round(bull_count/bear_count,2)))
        
        bull_comments = db[collection].find({map[classifier_name]:{"sentiment":"bullish"}})
        for comment in bull_comments:
            tt = comment['text'].encode('ascii','ignore').decode('unicode_escape')
            file1.write(tt.strip()+'\n')
        
        bear_comments = db[collection].find({map[classifier_name]:{"sentiment":"bearish"}})
        for bear in bear_comments:
            tt = bear['text'].encode('ascii','ignore').decode('unicode_escape')
            file2.write(tt.strip()+'\n')
        
        neutral_comments = db[collection].find({map[classifier_name]:{"sentiment":"neutral"}})
        for comment in neutral_comments:
            tt = comment['text'].encode('ascii','ignore').decode('unicode_escape')
            file3.write(tt.strip()+'\n')
        
        
if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()