import datetime
import argparse
import logging
import os
from pandas_datareader import data

logger = logging.getLogger(__name__)
download_symbols = ["SP500","GDP"]

start_date = {'year':2010,
              'day':1,
              'month':1
              }
end_date = {'year':2013,
              'day':27,
              'month':1
              }

def read_from_fred(download_symbols,start_date,end_date,output_dir):
    header_template = "Type FST_Hist\n" \
                      "Version 2.0\n" \
                      "Symbol {symbol}\n" \
                      "Name fred\n"

    start = datetime.datetime(start_date['year'],start_date['month'],start_date['day'])
    end = datetime.datetime(end_date['year'],end_date['month'],end_date['day'])
    logger.info("Reading from {start_date} to {end_date}".format(start_date=str(start_date),end_date=(str(end_date))))

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
                date = index.iloc[i].name.strftime("%d/%m/%Y")
                value = str(index.iloc[i][column])
                if value != 'nan':output.write("{date},{open},{high},{low},{close},{volume}\n".format(
                                                                                    date=date,open=value,
                                                                                    high=value,close=value,
                                                                                    low=value,volume='0'))
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
    read_from_fred(download_symbols,start_date,end_date,output_dir)

if __name__ == "__main__":
    main()