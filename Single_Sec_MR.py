class SingleSecurity_MeanReversion_Backtest(object):
    from datetime import datetime

    def __init__(self,df):

        self.data = df
        self.pnl_df = None
        self.pnl_arr = None

    def reindex(self,df):
        df = df.reset_index(inplace = False)
        df = df.iloc[:,1:]
        return(df)

    def format_(self):
        import datetime
        import numpy as np

        self.data = self.data.iloc[:,[n for n in range(len(list(self.data.columns))) if n != list(self.data.columns).index('Open Interest')]]

        self.data.loc[:,'Date'] = [datetime.datetime.strptime(i.split(' ')[0],"%m/%d/%Y").strftime('%d/%m/%Y') for i in self.data.loc[:,'Date']]

        if (datetime.datetime.strptime(self.data['Date'][0],'%d/%m/%Y').date() - datetime.datetime.strptime(self.data['Date'][1],'%d/%m/%Y').date()).days >= 0:
            self.data = self.reindex(self.data.iloc[self.data.index[::-1],:])

        self.data['Return'] = [np.nan] + [self.data['Close'][i+1] - self.data['Close'][i] for i in range(len(self.data)-1) if i != len(self.data)]


        temp = [np.nan] + [i for i in self.data['Close']]
        self.data['1d_lag'] = temp[:-1]
        self.data = self.reindex(self.data)

    def ADF(self,method):
        """Method specified is the constant and trend order to include in regression

        * 'c' : constant only (default)
        * 'ct' : constant and trend
        * 'ctt' : constant, and linear and quadratic trend
        * 'nc' : no constant, no trend"""
        import statsmodels
        from statsmodels.tsa.stattools import adfuller

        print('ADF Test Statistic:' + ' ' + str(adfuller(self.data['Close'],regression = method)[0]))
        print('-------------------')
        print('P-value:' + ' ' +str(adfuller(self.data['Close'],regression = method)[1]))
        print('-------------------')
        print('Number of lags used:' + ' ' +str(adfuller(self.data['Close'],regression = method)[2]))
        print('-------------------')
        test_stat = adfuller(self.data['Close'],regression = method)[0]
        if test_stat >= -3.1287988258407697:
            print('Cannot reject null hypothesis at any significant confidence level (1/5/10%)')
        elif test_stat < -3.1287988258407697 and test_stat >= -3.4134606257569886:
            print('Can reject null hypothesis with 90% confidence')
        elif test_stat < -3.4134606257569886 and test_stat >= -3.9648999792938597:
            print('Can reject null hypothesis with 95% confidence')
        elif test_stat < -3.9648999792938597:
            print('Can reject null hypothesis with 99% confidence')

    def setup(self):
        from scipy import stats
        import statsmodels.formula.api as smf
        import pandas as pd
        import re
        import numpy as np
        import MA_tools

        summary_df = pd.DataFrame({'y':self.data['Return'], 'x':self.data['1d_lag']})

        formula = 'y~x'
        result = smf.ols(formula, data=summary_df).fit()

        for i in [i for i in str(result.summary()).split(' ') if i != '']:
            if re.search(r'intercept',i,flags = re.I):
                beta = (float([i for i in str(result.summary()).split(' ') if i != ''][[i for i in str(result.summary()).split(' ') if i != ''].index(i)+1]))

        Lambda = abs(int(round(-np.log(2)/beta)))
        print('-------------------')
        print(f'Linear Mean Reversion Strategy with a {Lambda} day moving average window to inform market position')

        self.data['bt_std_ma'] = MA_tools.MA_tools().moving_average_std_dev(dataframe = self.data,name_of_column='1d_lag',days = Lambda)
        self.data['bt_ma'] = MA_tools.MA_tools().moving_average(dataframe = self.data,name_of_column='1d_lag',days = Lambda)

        mkt_position = []
        for i in range(len(self.data)):
            if self.data.loc[i,'bt_ma'] == np.nan:
                mkt_position.append(np.nan)
            else:
                mkt_position.append(-(self.data['1d_lag'][i] - self.data['bt_ma'][i])/self.data['bt_std_ma'][i])
        self.data['mkt_position'] = mkt_position


        pnl_df = self.reindex(self.data.iloc[self.data['mkt_position'].first_valid_index():,:])

        self.pnl_df = pnl_df

    def pnl(self,pnl_df):
        import numpy as np
        pnl_arr = []
        for n in range(len(pnl_df)):
            if n == 0:
                pnl_arr.append((pnl_df.Date[n],pnl_df.Return[n]*pnl_df.mkt_position[n],pnl_df.Return[n]*pnl_df.mkt_position[n]))
            else:
                pnl_arr.append((pnl_df.Date[n],np.sum([i[-1] for i in pnl_arr])+pnl_df.Return[n]*pnl_df.mkt_position[n],                                pnl_df.Return[n]*pnl_df.mkt_position[n]))
        self.pnl_arr = pnl_arr


    def visualize_strat(self,pnl_arr):
        import numpy as np
        import matplotlib.pyplot as plt

        plt.plot([i[0] for i in pnl_arr],[i[1] for i in pnl_arr])

        plt.xlabel('Date')
        plt.ylabel('P/L')

        plt.xticks(np.arange(0,len(pnl_arr),len(pnl_arr)/11),rotation = 300)

        plt.show()
