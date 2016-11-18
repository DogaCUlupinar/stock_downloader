import json
import argparse
import logging
import os
import pprint
import pandas as pd
pd.options.mode.chained_assignment = None
import stock_download.processors as prcs
import stock_download.downloaders as dwns

logger = logging.getLogger(__name__)


families = \
{
    'data_sources':['Pcr'],
    'Pcr':
    {
        'totalpc':
            {
                'symbol': 'totalpc',
                'download_symbol': 'totalpc',
                'output_filename': 'mytotalpc',
            },
        'indexpc':
            {
                'symbol': 'indexpc',
                'download_symbol': 'indexpc',
                'output_filename': 'indexpc',
            },
        'equitypc':
            {
                'symbol': 'equitypc',
                'download_symbol': 'equitypc',
                'output_filename': 'equitypc',
            },
        'etppc':
            {
                'symbol': 'etppc',
                'download_symbol': 'etppc',
                'output_filename': 'etppc',
            },
        'vixpc':
            {
                'symbol': 'vixpc',
                'download_symbol': 'vixpc',
                'output_filename': 'vixpc',
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
    'FRED':
        {
            'CPROFIT':
                {
                    'symbol': 'CPROFIT',
                    'download_symbol': 'CPROFIT',
                    'output_filename': 'cprofit'
                },
            'DFF':
                {
                    'symbol': 'DFF',
                    'download_symbol': 'DFF',
                    'output_filename': 'DFF'
                },
            'BAMLH0A0HYM2':
                {
                    'symbol': 'BAMLH0A0HYM2',
                    'download_symbol': 'BAMLH0A0HYM2',
                    'output_filename': 'BAMLH0A0HYM2'
                },
            'USSLIND':
                {
                    'symbol': 'USSLIND',
                    'download_symbol': 'USSLIND',
                    'output_filename': 'USSLIND'
                },
            'base_url': '{symbol}',
            'download_func': 'read_from_fred',
            'download_func_args': {'start': {'year':1972,'day':1,'month':1},'data_source':'fred'},
            'process_func': 'process_fred_default',
            'name': 'fred',
            'children': ['CPROFIT','DFF','BAMLH0A0HYM2','USSLIND']
        },
    'process_func_args': {},
    'download_func_args': {},
    'download_symbol': None
}

header_template = "Type FST_Hist\n" \
                  "Version 2.0\n" \
                  "Symbol {symbol}\n" \
                  "Name {name}\n"

def config_logger(logger,logging_level):
    logger.setLevel(logging_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def read_config():
    os.path.join(os.pardir,'configs')

def get_value(dic,family,child,key):
    try:
        return dic[family][child][key]
    except KeyError:
        try:
            return dic[family][key]
        except KeyError:
            return dic[key]

def runner(output_dir,families):
    for family in families['data_sources']:
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
            logger.info("Downloading using function {func} from url {url} and args {args}".format(
                func=download_func_name,url=url,args=pprint.pformat(download_func_args)
            ))

            #process
            process_func_name = get_value(families, family, child,'process_func')
            process_func_args = get_value(families,family,child,'process_func_args')
            process_func = getattr(prcs,process_func_name)
            logger.info("Processing using process function {func} using args {args}".format(
                func=process_func_name,args=pprint.pformat(process_func_args)
            ))
            df = process_func(df,**process_func_args)

            #write to file
            file_name = get_value(families,family,child,'output_filename') + ".day"
            file_path = os.path.join(output_dir, file_name)
            name = get_value(families,family,child,'name')
            logger.info("Writing symbol {symbol} to file {file_name}".format(
                symbol=symbol,file_name=file_path
            ))
            with open(file_path,'w') as output:
                #write the header
                output.write(header_template.format(symbol=symbol,name=name))
                output.write("# DATE,OPEN,HIGH,LOW,CLOSE,VOLUME\n")
                df.to_csv(output,sep=',',header=False,index=False,date_format="%m/%d/%Y",na_rep=0)

    print('DONE')


def main():
    families = read_config()
    config_logger(logger,logging.INFO)
    parser = argparse.ArgumentParser(
        description="download from data sources {names} and write to .day file".format(names=families['data_sources']))
    parser.add_argument("outdir", help="the directory to output the .day files")
    args = parser.parse_args()
    output_dir = args.outdir

    if os.path.exists(output_dir) == False:
        raise Exception("outdir {dr_name} does not exist".format(dr_name=output_dir))

    print("Downloading the following {downloads}".format(downloads=pprint.pformat({data_source: families[data_source]['children'] for data_source in families['data_sources']})))
    runner(output_dir,families)

if __name__ == "__main__":
    main()