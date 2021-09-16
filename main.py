# importing the required modules
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import  SentimentIntensityAnalyzer 
import pandas as pd
import matplotlib.pyplot as plt

# add url to get financial news
finviz_url="https://www.finviz.com/quote.ashx?t=" 

tickers = ['AMZN','AMD','FB']

news_tables ={}

for ticker in tickers:
    url = finviz_url+ticker

    req = Request(url=url, headers={'user-agent':'application'})
    response = urlopen(req)
    # print(response)

    html = BeautifulSoup(response,features="html.parser")
    # print(html)

    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

''' Commented as this was modularised

# print(news_tables)
#taking only amazon data
amzn_data=news_tables['AMZN']
amzn_rows=amzn_data.findAll('tr')
# print(amzn_rows)

#get text of all the rows
for index,row in enumerate(amzn_rows):
    title= row.a.text
    timestamp = row.td.text
    # print(timestamp+" "+title)
'''

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


# mean dataframe for particular date
#unstack the data
mean_df = df.groupby(['ticker','date']).mean().unstack()

# mean_df_df= mean_df
mean_df = mean_df.xs('compound',axis="columns").transpose()
# print(mean_df)

mean_df.plot(kind="bar")
plt.show()