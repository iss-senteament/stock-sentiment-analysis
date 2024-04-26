import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
from flask import Flask, render_template, request
from plotly.utils import PlotlyJSONEncoder

from sentiment.SentimentAnalysis import SentimentAnalysis
from yahoo_api import API
from datetime import datetime

EST = pytz.timezone('US/Eastern')


app = Flask(__name__)


def get_price_history(ticker: str, earliest_datetime: pd.Timestamp) -> pd.DataFrame:

    return API.get_price_history(ticker, earliest_datetime)
    

sentimentAlgo = SentimentAnalysis()

def get_news(ticker) -> pd.DataFrame:

    sentimentAlgo.set_symbol(ticker)
    api = API()
    df = api.get_news(ticker)
    return df
    #return API.get_news(ticker)


def calc_summary():
    df = sentimentAlgo.calc_summary()
    df = df.rename(columns={"positive_aggscore" : "Positive Aggscore",
                "neutral_aggscore" : "Neutral Aggscore",
                "negative_aggscore" : "Negative Aggscore",
                "positive_count" : "Positive Count",
                "neutral_count" : "Neutral Count",
                "negative_count" : "Negative Count",
                "recommend" : "Recommend"
                })
    
    #print(df.head(5))
    #sentimentAlgo.recommend()
    return df

def score_news(news_df: pd.DataFrame) -> pd.DataFrame:

    sentimentAlgo.set_data(news_df)
    sentimentAlgo.calc_sentiment_score()

    return sentimentAlgo.df


def plot_sentiment(df: pd.DataFrame, ticker: str) -> go.Figure:

    return sentimentAlgo.plot_sentiment()


def get_earliest_date(df: pd.DataFrame) -> pd.Timestamp:

    if len(df['Date Time']) > 0:
        date = df['Date Time'].iloc[-1]
        py_date = date.to_pydatetime()
        #return py_date.replace(tzinfo=EST)
        return py_date.astimezone(tz=EST) # To return the earliest time in EST
    else:
        return datetime.now(tz=EST)


def plot_hourly_price(df, ticker) -> go.Figure:

    fig = px.line(data_frame=df, x=df['Date Time'],
                  y="Price", title=f"{ticker} Price")
    return fig


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():

    ticker = request.form['ticker'].strip().upper()
    # 1. get news feed
    news_df = get_news(ticker)
    print(news_df.head(5))
    # 2. calculate sentiment scores
    scored_news_df = score_news(news_df)
    # 3. create a bar diagram
    fig_bar_sentiment = plot_sentiment(scored_news_df, ticker)
    graph_sentiment = json.dumps(fig_bar_sentiment, cls=PlotlyJSONEncoder)
    # 4. get earliest data time from the news data feed
    earliest_datetime = get_earliest_date(news_df)
    # 5. get price history for the ticker, ignore price history earlier than the news feed
    price_history_df = get_price_history(ticker, earliest_datetime)
    # 6. create a linear diagram
    fig_line_price_history = plot_hourly_price(price_history_df, ticker)
    graph_price = json.dumps(fig_line_price_history, cls=PlotlyJSONEncoder)
    # 7. Make the Headline column clickable
    # scored_news_df['Headline'] = scored_news_df['Headline'].apply(lambda title: f'<a href="{title[1]}">{title[0]}</a>')
    scored_news_df = convert_headline_to_link(scored_news_df)
    #scored_news_df = scored_news_df.drop(['sentiment_label', 'sentiment_score'], axis=1)
    scored_news_df = scored_news_df.rename(columns={"sentiment_label": "Sentiment Label",
                                                    "sentiment_score": "Sentiment Score",
                                                    })

    summary_df = calc_summary()

    # 8. render output
    scored_news_df.index = scored_news_df.index + 1
    summary_df.index = summary_df.index +1
    return render_template('analysis.html', ticker=ticker, graph_price=graph_price, 
                           graph_sentiment=graph_sentiment, 
                           table=scored_news_df.to_html(table_id='scored_news', classes='mystyle', render_links=True, escape=False),
                           #summary=summary_df.to_html(table_id='summary',classes='mystyle', render_links=True, escape=False)
                           summary=summary_df.to_json()
                           )


def convert_headline_to_link(df: pd.DataFrame) -> pd.DataFrame:

    df.insert(2, 'Headline', df['title + link'])

    # df['Headline'] = df['title + link']
    df.drop(columns = ['sentiment', 'title + link', 'title'], inplace=True, axis=1)

    return df


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True, load_dotenv=True)

