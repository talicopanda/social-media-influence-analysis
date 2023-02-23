from time import time
from data_manager import DataManager
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests


ts_df = pd.read_csv("./assets/mock_data.csv")
# data_set = Dataframe(influencer_supply_series, influencer_demand_series, periphery_supply_series, periphery_demand_series)
# time_series = [choose which time-series you want to compare]

def granger_causality_test(data, time_series):  
    # create dataframe to store output matrix    
    influence_df = pd.DataFrame(np.zeros((len(time_series), len(time_series))),columns=time_series, index=time_series)
    for col in influence_df.columns:
        for row in influence_df.index:
            # run grangercausalitytests against each pair of times_series
            test_result = grangercausalitytests(data[[row, col]], maxlag=12, verbose=False)
            
            # extract and format the values
            p_values = [round(test_result[i+1][0]['ssr_chi2test'][1],4) for i in range(12)]
            min_p_value = np.min(p_values)
            
            # populate the new df
            influence_df.loc[row, col] = min_p_value
    
    influence_df.columns = [var + '_x' for var in time_series]
    influence_df.index = [var + '_y' for var in time_series]
    return influence_df

# print(granger_causality_test(ts_df, time_series = ts_df.columns))