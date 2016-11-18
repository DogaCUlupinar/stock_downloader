import pandas as pd
import datetime
from pandas_datareader import data
import logging
import pprint

logger = logging.getLogger(__name__)
pd.options.mode.chained_assignment = None


def read_csv_from_url(url,**kwargs):
    df = pd.read_csv(url,**kwargs)
    logger.debug("Downloading from {url} with parameters {param}",url=url,parameters=pprint.pformat(kwargs))
    return df


def read_from_fred(download_symbol,**kwargs):

    end = kwargs.get('end',datetime.datetime.now())
    start = kwargs.get('start',{'year':1972,'day':1,'month':1})
    start = datetime.datetime(start['year'],start['month'],start['day'])
    data_source = kwargs.get('data_source','fred')
    logger.debug("Downlading {download_symbol} from {data_source} within in time {start} to {end}".format(
                 download_symbol=download_symbol,data_source=data_source,end=end,start=start))
    df = data.DataReader(download_symbol,data_source,start,end)

    return df
