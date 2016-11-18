import pandas as pd
import datetime
import logging

pd.options.mode.chained_assignment = None
logger = logging.getLogger(__name__)

def add_last_date(dataframe):
    last_date = dataframe["DATE"].iloc[-1].strftime("%m/%d/%Y")

    if last_date != datetime.datetime.now().strftime("%m/%d/%Y"):
        extra_row = dataframe.iloc[-1]
        extra_row.loc['DATE'] = datetime.datetime.now()
        dataframe = dataframe.append(extra_row, ignore_index=True)

    return dataframe


def process_time(dataframe,**kwargs):

    dataframe["DATE"] = pd.to_datetime(dataframe['DATE'], **kwargs)
    dataframe.sort_values(by=["DATE"], inplace=True)

    return add_last_date(dataframe)

def process_pcr_default(dataframe,**kwargs):

    dataframe["VOLUME"] = pd.Series(0,dataframe.index)
    dataframe.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    return process_time(dataframe,**kwargs)

def process_naim_default(dataframe,**kwargs):
    dataframe = dataframe[['Date','Quart 1 (25% at/below)','Quart 2 (median)', 'Quart 3 (25% at/above)','Mean/Average']]
    dataframe["VOLUME"] = pd.Series(0, dataframe.index)
    dataframe.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    return process_time(dataframe,**kwargs)


def process_fred_default(dataframe,**kwargs):

    dataframe.insert(0,'DATE',dataframe.index)
    dataframe.insert(1,'HIGH',dataframe.iloc[:,1])
    dataframe.insert(1,'LOW',dataframe.iloc[:,1])
    dataframe.insert(1,'close',dataframe.iloc[:,1])
    dataframe.insert(5,'volume',0)

    dataframe.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
    dataframe.sort_values(by=["DATE"], inplace=True)

    return add_last_date(dataframe)

def process_margin_default(dataframe,**kwargs):

    dataframe = dataframe[[0,3,1]]
    dataframe.insert(2,"High",0)
    dataframe.insert(2,"low",0)
    dataframe.insert(5,"volume",0)
    dataframe.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']


    return process_time(dataframe,**kwargs)