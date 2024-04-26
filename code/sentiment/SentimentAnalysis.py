from transformers import pipeline,AutoTokenizer, AutoModelForSequenceClassification
from .SentimentAnalysisBase import SentimentAnalysisBase
import pandas as pd
import joblib
from config import config


class SentimentAnalysis (SentimentAnalysisBase):

    def __init__(self):

        print('Loading Tokenizer : ' , config.TOKENIZER)
        tokenizer = AutoTokenizer.from_pretrained(config.TOKENIZER)
        print('Loading Model : ' , config.MODEL)
        model = AutoModelForSequenceClassification.from_pretrained(config.MODEL)
        self._sentiment_analysis  = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
        
        self.model = joblib.load('senTEAMentanalysis.pkl')
        super().__init__()

    def calc_sentiment_score(self):

        self.df['sentiment'] = self.df['title'].apply(self._sentiment_analysis)
        #print(self.df.head(8))
        self.df['sentiment_label'] = self.df['sentiment'].apply(lambda x : x[0]["label"])
        #print(self.df.head(8))
        self.df['sentiment_score'] = round(self.df['sentiment'].apply(
            lambda x: {x[0]['label'] == 'negative': -1, x[0]['label'] == 'positive': 1}.get(True, 0) * x[0]['score']),3)

    def calc_summary(self):
        positive_count=[]
        positive_aggscore=[]
        neutral_count=[]
        neutral_aggscore=[]
        negative_count=[]
        negative_aggscore=[]

        positive_row = self.df[self.df.sentiment_label.str.lower() == "positive"]
        positive_aggscore.append(positive_row["sentiment_score"].sum())
        positive_count.append(len(positive_row))
        
        neutral_row = self.df[self.df.sentiment_label.str.lower() == "neutral"]
        neutral_aggscore.append(neutral_row["sentiment_score"].sum())
        neutral_count.append(len(neutral_row))

        negative_row = self.df[self.df.sentiment_label.str.lower() == "negative"]
        negative_aggscore.append(negative_row["sentiment_score"].sum())
        negative_count.append(len(negative_row))
        
        self.summary_df = pd.DataFrame({'positive_aggscore': positive_aggscore, 'neutral_aggscore': neutral_aggscore,  'negative_aggscore': negative_aggscore,'positive_count': positive_count,'neutral_count': neutral_count, "negative_count": negative_count})
        
        d = {'0': 'Buy', '1': 'Hold', '2': 'Sell'}
        result = self.model.predict(self.summary_df)
        resultStr = d.get(str(result[0]))
        r = pd.DataFrame({'recommend': [resultStr]})
        self.summary_df2 = pd.concat([self.summary_df,r['recommend']], axis=1)
        return self.summary_df2
    

