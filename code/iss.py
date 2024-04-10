import pandas as pd
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class Senteament():
    def __init__(self):
        tokenizer = AutoTokenizer.from_pretrained("soleimanian/financial-roberta-large-sentiment")
        model = AutoModelForSequenceClassification.from_pretrained("soleimanian/financial-roberta-large-sentiment")
        self._sentiment_analysis  = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
       

    def set_data(self, df):
        self.df = df

    def calc_sentiment_score(self):
        self.df['sentiment'] = self.df['title'].apply(self._sentiment_analysis)
        return self.df