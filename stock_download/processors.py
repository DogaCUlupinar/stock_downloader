import pandas as pd
import datetime
pd.options.mode.chained_assignment = None

def process_time(dataframe,**kwargs):

    dataframe["DATE"] = pd.to_datetime(dataframe['DATE'], **kwargs)
    dataframe.sort_values(by=["DATE"], inplace=True)

    last_date = dataframe["DATE"].iloc[-1].strftime("%m/%d/%Y")

    if last_date != datetime.datetime.now().strftime("%m/%d/%Y"):
        extra_row = dataframe.iloc[-1]
        extra_row.loc['DATE'] = datetime.datetime.now()
        dataframe = dataframe.append(extra_row, ignore_index=True)

    return dataframe

def process_pcr_default(dataframe,**kwargs):

    dataframe["VOLUME"] = pd.Series(0,dataframe.index)
    dataframe.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    return process_time(dataframe,**kwargs)

def process_naim_default(dataframe,**kwargs):
    dataframe = dataframe[['Date','Quart 1 (25% at/below)','Quart 2 (median)', 'Quart 3 (25% at/above)','Mean/Average']]
    dataframe["VOLUME"] = pd.Series(0, dataframe.index)
    dataframe.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    return process_time(dataframe,**kwargs)