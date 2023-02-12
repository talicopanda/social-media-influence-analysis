from data_manager import DataManager
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests


#data provided by data_manager.py

# data = Dataframe(influencer_supply_series, influencer_demand_series, periphery_supply_series, periphery_demand_series)
# varaibles = [choose which time-series you want to compare]

def granger_causality_test(data_set, time_series, lag):  
    # create dataframe to store output matrix  
    df = pd.DataFrame(np.zeros((len(time_series), len(time_series))), columns=time_series, index=time_series)
    
    #Run grangercausalitytests against each times_series
    for column in df.columns:
        for row in df.index:
            
            test_result = grangercausalitytests(data_set[[row, column]], lag)
            
            # extract and format p-values to get the correlation between chosen data-sets
            p_values = [round(test_result[i+1][0]['ssr_ftest'][1],4) for i in range(3)]
            
            # return causlity result
            min_p_value = np.min(p_values)
            df.loc[row, column] = min_p_value

    df.columns = [var + '_cause' for var in time_series]
    df.index = [var + '_against' for var in time_series]
    return df