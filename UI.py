# -*- coding: utf-8 -*-

# Run this app with `python UI.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import  SentimentIntensityAnalyzer 
import matplotlib.pyplot as plt

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'SAVSN | Dashboard' 
app.layout = html.Div([
   
    html.H2("Sentimental Analysis & Visualization of Stock News", style={"textAlign": "center"}),
   
    dcc.Tabs(id="tabs", children=[
       
        
        dcc.Tab(label='SAVSN', children=[
            html.Div([
                html.H5("Select the company", 
                        style={'textAlign': 'center'}),
              
              dcc.Dropdown(id='my-url-dropdown',
                             options=[{'label': 'https://www.finviz.com/quote.ashx?t=', 'value': 'https://www.finviz.com/quote.ashx?t='}], 
                             value='https://www.finviz.com/quote.ashx?t=',
                             disabled=True,
                             style={"display": "block", "margin-left": "auto", 
                                    "margin-right": "auto", "width": "60%"}),

                dcc.Dropdown(id='my-dropdown',
                             options=[{'label': 'Amazon', 'value': 'AMZN'},
                                      {'label': 'AMD Company', 'value': 'AMD'},
                                      {'label': 'Google', 'value': 'GOOG'},
                                      {'label': 'Tesla', 'value': 'TSLA'},
                                      {'label': 'Apple','value': 'AAPL'}, 
                                      {'label': 'Facebook', 'value': 'FB'}, 
                                      {'label': 'Microsoft','value': 'MSFT'}], 
                             multi=True,value=['AAPL','GOOG','FB'],
                             style={"display": "block", "margin-left": "auto", 
                                    "margin-right": "auto", "width": "60%"}),
                dcc.Graph(id='highlow'),         
             
            ], className="container"),
        ])


    ])
])


@app.callback(Output('highlow', 'figure'),
              [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown):
    finviz_url="https://www.finviz.com/quote.ashx?t=" 
    print(selected_dropdown)
    tickers = selected_dropdown

    news_tables ={}

    for ticker in tickers:
        url=finviz_url+ticker

        req = Request(url=url, headers={'user-agent':'application'})
        response = urlopen(req)
        # print(response)

        html = BeautifulSoup(response,features="html.parser")
        # print(html)

        news_table = html.find(id='news-table')
        news_tables[ticker]=news_table

    
    parsed_data = []
    #handles for all items in the news tables to obtain the date time and title
    for ticker,news_table in news_tables.items():
        for row in news_table.findAll('tr'):
            title = row.a.text

            date_data = row.td.text.split(' ')

            if len(date_data)==1:
                time = date_data[0]
            else:
                date = date_data[0]
                time=date_data[1]

            parsed_data.append([ticker,date,time, title])  

    # print(parsed_data)

    #create a dataframe to host the array
    df = pd.DataFrame(parsed_data,columns=['ticker','date','time','title'])
    # print(df.head())

    vader = SentimentIntensityAnalyzer()
    # print(vader.polarity_scores("I think Apple is bad company.They will fail."))

    lambda_function = lambda title: vader.polarity_scores(title)['compound']
    df['compound'] =df['title'].apply(lambda_function)

    # print(df.head())

    df['date'] =pd.to_datetime(df.date).dt.date

    # df = pd.DataFrame({
    # "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    # "Amount": [4, 1, 2, 2, 4, 5],
    # "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    # })

    fig = px.bar(df, x="date", y="compound", color="ticker", barmode="group")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)