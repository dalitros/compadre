import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose


def decompose_signal(df=pd.DataFrame(), signal=None):
    if df.empty:
        raise ValueError('DataFrame is empty')
    if signal is None:
        raise ValueError('Signal is empty')
    hr = [40, 50, 60, 70, 80]
    for h in hr:
        period = np.round((h / 60) * 8)
        period = round(period.astype(float))
        series = df[signal]  # Pick led color
        #My addition starts here.
        previous_value = np.nan

        # Replace NaN values with previous non-NaN value or a statistically less harmful value
        # for i in range(len(series)):
        #     if np.isnan(series[i]):
        #         if not np.isnan(previous_value):
        #             series[i] = previous_value
        #         else:
        #             # Implement a statistical method to impute NaN values, such as mean, median, or mode
        #             series[i] = np.mean(series[~np.isnan(series)])
        #End of my addition - back to original code from now on
        series = series.astype(int)
        seasonal_decomposition = seasonal_decompose(
            series, period=period, model='additive')
        df['ppg' + '_season_' +
            str(h)] = pd.DataFrame(seasonal_decomposition.seasonal)
        df[str(signal) + '_trend'] = pd.DataFrame(seasonal_decomposition.trend)
        df[str(signal) + '_resid'] = pd.DataFrame(seasonal_decomposition.resid)
    return seasonal_decomposition, df
