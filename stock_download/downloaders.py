import pandas as pd
pd.options.mode.chained_assignment = None

def read_csv_from_url(url,**kwargs):
    df = pd.read_csv(url,**kwargs)
    return df

