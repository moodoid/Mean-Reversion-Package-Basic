import Single_Sec_MR
import pandas as pd
import matplotlib as plt
from os import listdir
from os.path import isfile, join
import re
import pandas as pd
import MA_tools
def auto_format_df(df):
    columns = []
    for i in df.columns:
        columns.append(i)
    const_dic = {}
    for i in columns:
        const_dic[i] = [i]
    fill_df = pd.DataFrame(data = const_dic,columns = columns)

    df = pd.concat([fill_df,df])

    column_dic = {columns[0]:'Date',columns[1]:'Close',columns[2]:'Open',columns[3]:'High',columns[4]:'Low',columns[5]:'Volume',columns[6]: 'Open Interest'}


    df = df.rename(columns = column_dic)
    df = reindex(df)
    for n in range(len(df)):
        for j in df.columns[1:]:
            if type(df[j][n]) == str:
                df[j][n] = float(df[j][n])

    return(df)

def reindex(df):
    df = df.reset_index(inplace = False)
    df = df.iloc[:,1:]
    return(df)

mypath = r"C:\Users\Boris\Desktop\Files"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for i in onlyfiles:
    if re.search('gld',str(i),flags = re.I):
        gld = auto_format_df(pd.read_csv(mypath + r"//" + i,delimiter = ';'))
    elif re.search('gdx',str(i),flags = re.I):
        gdx = auto_format_df(pd.read_csv(mypath + r"//" + i,delimiter = ';'))

test = Single_Sec_MR.SingleSecurity_MeanReversion_Backtest(gdx)

test.format_()
test.ADF('ct')
test.setup()
test.pnl(test.pnl_df)
test.visualize_strat(test.pnl_arr)
