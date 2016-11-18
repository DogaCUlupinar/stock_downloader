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
    file_path = os.path.join(os.pardir,'configs','download_config.json')
    with open(file_path,'r') as f:
        return json.load(f)

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