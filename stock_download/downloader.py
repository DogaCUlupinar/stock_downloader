import datetime
import argparse
import logging
import os
from pandas_datareader import data
import pandas as pd
pd.options.mode.chained_assignment = None
import stock_download.processors as prcs
import stock_download.downloaders as dwns

logger = logging.getLogger(__name__)
download_symbols = ["CPROFIT","DFF", "BAMLH0A0HYM2", "USSLIND"]

start_date = {'year':1972,
              'day':1,
              'month':1
              }

families = \
{
    'Pcr':
    {
        'totalpc':
            {
                'symbol': 'totalpc',
                'download_symbol': 'totalpc',
                'output_filename': 'mytotalpc',
                'download_func': 'read_csv_from_url'
            },
        'indexpc':
            {
                'symbol': 'indexpc',
                'download_symbol': 'indexpc',
                'output_filename': 'indexpc',
                'download_func': 'read_csv_from_url'
            },
        'equitypc':
            {
                'symbol': 'equitypc',
                'download_symbol': 'equitypc',
                'output_filename': 'equitypc',
                'download_func': 'read_csv_from_url'
            },
        'etppc':
            {
                'symbol': 'etppc',
                'download_symbol': 'etppc',
                'output_filename': 'etppc',
                'download_func': 'read_csv_from_url'
            },
        'vixpc':
            {
                'symbol': 'vixpc',
                'download_symbol': 'vixpc',
                'output_filename': 'vixpc',
                'download_func': 'read_csv_from_url'
            },
        'base_url': 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/{symbol}.csv',
        'download_func': 'read_csv_from_url',
        'download_func_args': {'skiprows': 2},
        'process_func': 'process_pcr_default',
        'process_func_args': {'format':"%m/%d/%Y"},
        'name':'Pcr',
        'children': ['totalpc','indexpc','equitypc','etppc','vixpc']
    },
    'Aaii':
        {
            'sentiment':
                {
                    'symbol':'sentiment',
                    'output_filename': 'sentiment'
                },
            'base_url': 'http://www.aaii.com/files/surveys/{symbol}.xls',
            'download_func': 'read_xls_from_url'
        },
    'NAIM':
        {
            'naim':
                {
                    'symbol':'naim',
                    'download_symbol': 'export',
                    'output_filename':'naim'
                },
            'base_url':'http://www.naaim.org/wp-content/plugins/ip-chart/{symbol}.php',
            'download_func': 'read_csv_from_url',
            'process_func': 'process_naim_default',
            'process_func_args': {'format':"%m/%d/%Y"},
            'name': 'naim',
            'children': ['naim']
        },
    'MARGIN':
        {
            'margin':
                {
                    'symbol':'naim',
                    'output_filename':'margin'
                },
            'base_url': 'http://www.nyxdata.com/nysedata/asp/factbook/table_export_csv.asp?mode=tables&key=50',
            'download_func': 'read_csv_from_url',
            'download_func_args': {'sep':"\t|\s",'skiprows':4,'header':None,'engine':'python'},
            'process_func':'process_margin_default',
            'process_func_args':{'format':"%m/%Y"},
            'name': 'naim',
            'children': ['margin']
        },
    'download_func_args': {},
    'download_symbol' : None
}


header_template = "Type FST_Hist\n" \
                  "Version 2.0\n" \
                  "Symbol {symbol}\n" \
                  "Name {name}\n"

def read_from_fred(download_symbols,start_date,output_dir):
    header_template = "Type FST_Hist\n" \
                      "Version 2.0\n" \
                      "Symbol {symbol}\n" \
                      "Name fred\n"

    start = datetime.datetime(start_date['year'],start_date['month'],start_date['day'])
    end = datetime.datetime.now()
    logger.info("Reading from {start_date} to {end_date}".format(start_date=str(start_date),end_date=(str(end))))

    index = data.DataReader(download_symbols,"fred",start,end)
    logger.info("Reading for the following indices: %s" %(str(index.columns)))

    for column in index.columns:
        filename = "{0}.day".format(column)
        file_path = os.path.join(output_dir,filename)
        with open(file_path,'w') as output:
            logger.info("writing data to %s" % (file_path))
            #write the header
            output.write(header_template.format(symbol=column))
            output.write("# DATE,OPEN,HIGH,LOW,CLOSE,VOLUME\n")
            for i in range(index.shape[0]):
                date = index.iloc[i].name.strftime("%m/%d/%Y")
                value = str(index.iloc[i][column])
                if value != 'nan':
                    last_value = value
                    output.write("{date},{open},{high},{low},{close},{volume}\n".format(
                                                                                    date=date,open=value,
                                                                                    high=value,close=value,
                                                                                    low=value,volume='0'))
            date = end.strftime("%m/%d/%Y")
            output.write("{date},{open},{high},{low},{close},{volume}\n".format(
                date=date, open=last_value,
                high=last_value, close=last_value,
                low=last_value, volume='0'))
    logger.info("Done")

def config_logger(logger,logging_level):
    logger.setLevel(logging_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def main():
    config_logger(logger,logging.INFO)
    parser = argparse.ArgumentParser(
        description="download from fred {names} and write to .day file".format(names=download_symbols))
    parser.add_argument("outdir", help="the directory to output the .day files")
    args = parser.parse_args()
    output_dir = args.outdir
    if os.path.exists(output_dir) == False:
        raise Exception("outdir {dr_name} does not exist".format(dr_name=output_dir))
    read_from_fred(download_symbols,start_date,output_dir)

def get_value(dic,family,child,key):
    try:
        return dic[family][child][key]
    except KeyError:
        try:
            return dic[family][key]
        except KeyError:
            return dic[key]

def main_test():
    family = 'MARGIN'
    for child in families[family]['children']:
        #download
        download_func_name = get_value(families,family,child,'download_func')
        download_func_args = get_value(families,family,child,'download_func_args')
        download_func = getattr(dwns,download_func_name)

        base_url = get_value(families,family,child,'base_url')
        download_symbol = get_value(families,family,child,'download_symbol')
        symbol = get_value(families,family,child,'symbol')
        url= base_url.format(symbol=download_symbol)
        df = download_func(url,**download_func_args)

        #process
        process_func_name = get_value(families, family, child,'process_func')
        process_func_args = get_value(families,family,child,'process_func_args')
        process_func = getattr(prcs,process_func_name)

        df = process_func(df)
        df = prcs.process_time(df,**process_func_args)

        #write to file
        file_name = get_value(families,family,child,'output_filename') + ".day"
        name = get_value(families,family,child,'name')

        with open(file_name,'w') as output:
            #write the header
            output.write(header_template.format(symbol=symbol,name=name))
            output.write("# DATE,OPEN,HIGH,LOW,CLOSE,VOLUME\n")
            df.to_csv(output,sep=',',header=False,index=False,date_format="%m/%d/%Y",na_rep=0)

    print('done')

if __name__ == "__main__":
    main_test()