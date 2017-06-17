#==============================================================================
# This file deals with the webpage side of things. It handles the POST/GET 
# methods and renders the webpage accordingly.
#==============================================================================

## Imports.
from flask import Flask, render_template, request, redirect
import pandas as pd
from bokehPlot import create_bokeh_plot
#import os

## Declares the app.
app = Flask(__name__)

## Reads the data.
tickers = pd.read_csv('https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/WIKI_tickers.csv')


## Main entrance point for the app. Redirects to /index route.
## The '/' shows the suffix of the web page (e.g. localhost:port/)
@app.route('/')
def main():
    return redirect('/index')

## Renders the index.html which is the main page of the app.
@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    The main page of the app.

    POST: Validate input symbol and create the heroku plot.

    GET: Load the search bar.        
    """
    if request.method == 'POST' and 'symbol' in request.form:
        symbl = request.form['symbol'].upper()
        dataselect = request.form['dataselect']
        if 'WIKI/' + symbl in tickers['quandl code'].values:
            try:
                name = tickers.loc[tickers['quandl code'] ==
                                   'WIKI/' + symbl, 'name'].iloc[0]
                script, div = create_bokeh_plot(symbl, name, dataselect)
                return render_template('index.html', place_holder='Input Stock Symbol...',
                                       plot_script=script, plot_div=div)
            except:
                return render_template('index.html',
                                       place_holder='An error has occured.')
        else:
            return render_template('index.html',
                                       place_holder='Stock Symbol not recognized. Please try again...') 
    else:
       ## Render the index.html and replace the place holder value with
       ## the provided string. 
       return render_template('index.html', place_holder='Input Stock Symbol...')

## Runs the app.
if __name__ == '__main__':
  app.run(port=33507)
#  port = int(os.environ.get("PORT", 5000))
#  app.run(host='0.0.0.0', port=port)
