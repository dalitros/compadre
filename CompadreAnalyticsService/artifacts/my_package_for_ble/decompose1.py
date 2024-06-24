import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

#Decomposition of data
# def main ():
# Decomposition with periods of 40-80. for 300 lines analysis to use in feature_eng().
def decompos_signal(df=None, signal=None):
    hr = [40, 50, 60, 70, 80]
    for h in hr:
        #     period=np.round(df['HR'].mean()/60*32)
        period = np.round((h / 60) * 8)
        period = round(period.astype(float))
        series = df[signal]  # Pick led color
        series = series.astype(int)
        seas_decomp = seasonal_decompose(series, period=period, model='additive')
        #             fig = seas_decomp.plot()
        df['ppg' + '_season_' + str(h)] = pd.DataFrame(seas_decomp.seasonal)
        df[str(signal) + '_trend'] = pd.DataFrame(seas_decomp.trend)
        df[str(signal) + '_resid'] = pd.DataFrame(seas_decomp.resid)
    #             print("Heart Rate ",h,"Period",period)
    return seas_decomp, df

# Decomposition with periods of 10. for analysis of at least 20 lines.
def decompos_signal1(df=None, signal=None):
    hr = [10]
    for h in hr:
        #     period=np.round(df['HR'].mean()/60*32)
        period = np.round((h / 60) * 8)
        period = round(period.astype(float))
        series = df[signal]  # Pick led color
        series = series.astype(int)
        seas_decomp = seasonal_decompose(series, period=period, model='additive')
        #             fig = seas_decomp.plot()
        df['ppg' + '_season_' + str(h)] = pd.DataFrame(seas_decomp.seasonal)
        df[str(signal) + '_trend'] = pd.DataFrame(seas_decomp.trend)
        df[str(signal) + '_resid'] = pd.DataFrame(seas_decomp.resid)
    #             print("Heart Rate ",h,"Period",period)
    return seas_decomp, df