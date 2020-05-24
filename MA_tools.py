git init
class MA_tools(object):

    def __init__(self):
        pass
    def moving_average(self,dataframe,name_of_column,days):
        import numpy as np
        import pandas as pd
        temp = []
        for i in range(len(dataframe)):
            if i < days:
                temp.append(np.nan)
            else:
                num = 0
                for j in range(days):
                    num += dataframe[name_of_column][i-j]
                temp.append(num/days)
        return(temp)

    def moving_average_std_dev(self,dataframe,name_of_column,days):
        import numpy as np
        import pandas as pd
        temp = []
        for i in range(len(dataframe)):
            if i < days:
                temp.append(np.nan)
            else:
                num = 0
                TEMP = []
                for j in range(days):
                    TEMP.append(dataframe[name_of_column][i-j])
                temp.append(np.std(TEMP))
        return(temp)
