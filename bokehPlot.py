# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 09:46:35 2017

@author: heinzlugo
"""

#==============================================================================
# This file deals with the bokeh plot functionality side of things.
#==============================================================================

## Imports.
from flask import Markup
import requests
import datetime

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import NumeralTickFormatter

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

## Gets the data to be plotted in the bokeh plot.
def get_data(symbl, parameter):
    """
    Method for requesting data from quandl api. The data gathered is set to
    30 day intervals from the current date.
    Args:
            symbl: Valid stock ticker symbol.
            parameter: Information to be shown.
    Returns:
            {date, closing price}
    """
    ## API session 
    end_date = datetime.datetime.now()
    start_date = end_date + datetime.timedelta(-30)
    api_url = 'https://www.quandl.com/api/v3/datasets/WIKI/%s.json?api_key=t-drH_WSpLdRenh1o86E&start_date=%s&end_date=%s' \
        % (symbl, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    
    ## raw_json returns a dictionary from which the data with 'dataset' key
    ## is recovered. This is in itself a dictionary. 
    raw_json = session.get(api_url).json()['dataset']
    ## The data frame which will serve as data source for the bokeh plot is
    ## created here. The raw_json['data'] is a list of lists in which position
    ## 0 stores the date as a string and position 1, 4, 8 and 11 store the
    ## opening, closing, adjusted opening and adjusted closing prices respectively.
    if parameter == 'Opening price':
        index = 1
    elif parameter == 'Closing price':
        index = 4
    elif parameter == 'Adjusted opening price':
        index = 8
    elif parameter == 'Adjusted closing price':
        index = 11
        
    df = pd.DataFrame({
        'date': [x[0] for x in raw_json['data']],
        'close': np.array([x[index] for x in raw_json['data']]),
    })
    df['date'] = pd.to_datetime(df['date'])
    return df
    
## Plots the data in the bokeh plot.
def create_bokeh_plot(symbl, name, parameter):
    """
    Method for creating bokeh plot
    Args:
            symbl: Valid stock ticker symbol.
            name: Company name, used for plot title.
            parameter: Information to be shown.
    Returns:
            (script, div) bokeh script and div markup
    """
    ## Creates the figure.
    plot = figure(title=name, tools='wheel_zoom, pan',
                  responsive=True, plot_width=1000,
                  plot_height=500, x_axis_type='datetime')
    ## Retrieves the data as a dataframe for plotting.
    df = get_data(symbl, parameter)
    ## Create simple linear regression model.
    df['ticks'] = range(0, len(df.index.values))
    X = df.drop(['close','date'], axis = 1)
    regr = LinearRegression()
    regr.fit(X, df['close'])
    ## Creates the plot.
    plot.line(df['date'], df['close'], legend=parameter)
    plot.circle(df['date'], df['close'], legend=parameter)
    plot.line(df['date'], regr.predict(X), legend='Fit', line_color = "red", line_dash="4 4")
    plot.legend.location = 'top_left'
    plot.legend.orientation = 'horizontal'
    plot.legend.background_fill_alpha = 0.0
    plot.yaxis[0].formatter = NumeralTickFormatter(format='$0.00')
    script, div = components(plot)
    return Markup(script), Markup(div)