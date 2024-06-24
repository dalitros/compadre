import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from model.decompose import decompose_signal
import logging


XGBR1 = xgb.XGBRegressor()
model_path = 'model/acc15.json'
XGBR1.load_model(model_path)
SCALER = MinMaxScaler()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def scale_data(df=pd.DataFrame()):
    if df.empty:
        raise ValueError('DataFrame is empty')
    features = [
        'Ax', 'Ay', 'Az',
        'green',
        'acc_x_diff', 'acc_y_diff', 'acc_z_diff',
        'vec_acc_diff', 'vec_acc',
        'ppg_season_40', 'ppg_season_50', 'ppg_season_60', 'ppg_season_70', 'ppg_season_80',
    ]
    result = df[features]

    result = SCALER.fit_transform(result)
    result = pd.DataFrame(result, columns=[
        'Ax', 'Ay', 'Az',
        'green',
        'acc_x_diff', 'acc_y_diff', 'acc_z_diff',
        'vec_acc_diff', 'vec_acc',
        'ppg_season_40', 'ppg_season_50', 'ppg_season_60', 'ppg_season_70', 'ppg_season_80',
    ])
    return result


def transform(dat=pd.DataFrame()):
    if dat.empty:
        raise ValueError('DataFrame is empty')
    # if len(dat) < 300:
    #     raise ValueError('DataFrame must have at least 300 rows')
    # ,file_name=None):#,signal=None):
    # dat = pd.read_csv(file)
    # New Features based on data

    signals = ['IR', 'Red', 'green']
    for signal in signals:
        _, dat = decompose_signal(df=dat, signal=signal)

    dat = dat.fillna(method="bfill")
    dat['IR_diff'] = dat['IR'].diff()
    dat['Red_diff'] = dat['Red'].diff()
    dat['green_diff'] = dat['green'].diff()
    dat['acc_x_diff'] = dat['Ax'].diff()
    dat['acc_y_diff'] = dat['Ay'].diff()
    dat['acc_z_diff'] = dat['Az'].diff()
    dat['g_x_diff'] = dat['Gx'].diff()
    dat['g_y_diff'] = dat['Gy'].diff()
    dat['g_z_diff'] = dat['Gz'].diff()
    dat['IR_diff'] = dat['IR'].diff()
    dat['vec_acc'] = np.sqrt(
        (dat['Ax'] ** 2) + (dat['Ay'] ** 2) + (dat['Az'] ** 2))  # (meters)
    dat['vec_g'] = np.sqrt(
        (dat['Gx'] ** 2) + (dat['Gy'] ** 2) + (dat['Gz'] ** 2))  # (meters)
    dat['vec_acc_diff'] = dat['vec_acc'].diff()
    dat['vec_g_diff'] = dat['vec_g'].diff()
    dat = dat[~(dat.isnull().any(axis=1))]  # to remove nan
    dat = dat[~(dat.isin([np.inf, -np.inf]).any(axis=1))]  # to remove inf
    dat = dat.reset_index(drop=True)

    # Predict
    scaled_data = scale_data(dat)
    predictions = pd.DataFrame(np.round(XGBR1.predict(scaled_data)))
    dat = pd.concat([dat, predictions], axis=1)

    # Other feature engineering
    scaler = MinMaxScaler(feature_range=(0, 1))
    dat['vec_g_roll'] = dat['vec_g'].rolling(10).mean()
    dat['Tilt_range'] = dat['vec_g_roll'] * 100 / 2000
    dat['zeros'] = 0

    dat['green_trend1'] = dat['green_trend']
    dat['Red_trend1'] = dat['Red_trend']
    dat['IR_trend1'] = dat['IR_trend']
    dat['green_trend1'] = dat['green_trend1'].fillna(
        dat['green'])  # , inplace=True)
    dat['Red_trend1'] = dat['Red_trend1'].fillna(dat['Red'])  # , inplace=True)
    dat['IR_trend1'] = dat['IR_trend1'].fillna(dat['IR'])  # , inplace=True)

    dat['green_range'] = scaler.fit_transform(dat[['green_trend1']])
    dat['Red_range'] = scaler.fit_transform(dat[['Red_trend1']])
    dat['IR_range'] = scaler.fit_transform(dat[['IR_trend1']])
    green_base = dat['green_range'][0:10].mean()
    Red_base = dat['Red_range'][0:10].mean()
    IR_base = dat['IR_range'][0:10].mean()

    dat['red_ir_range_ratio'] = dat['Red_range'] / dat['IR_range']
    dat['red_green_range_ratio'] = dat['Red_range'] / dat['green_range']
    dat['ir_green_range_ratio'] = dat['IR_range'] / dat['green_range']

    dat['red_ir_ratio'] = dat['Red'] / dat['IR']
    dat['red_green_ratio'] = dat['Red'] / dat['green']
    dat['ir_green_ratio'] = dat['IR'] / dat['green']
    dat['movement1'] = np.where((dat['vec_acc_diff'] >= 1000) | (
        dat['vec_acc_diff'] <= -1000), 1, 0)
    dat['movement2'] = np.where((dat['vec_acc_diff'] >= 110) | (
        dat['vec_acc_diff'] <= -110), 1, 0)
    dat['tilt1'] = np.where((dat['vec_g_diff'] > 200) |
                            (dat['vec_g_diff'] < -200), 1, 0)
    dat['tilt2'] = np.where((dat['vec_g_diff'] > 100) |
                            (dat['vec_g_diff'] < -100), 1, 0)
    dat['vec_acc_diff_roll'] = abs(dat['vec_acc_diff']).rolling(10).mean()

    scaler = MinMaxScaler(feature_range=(0, 1))
    dat['acc_range'] = dat['vec_acc_diff_roll'] * 100 / 20000
    #     dat['acc_range'] = scaler.fit_transform(dat[['vec_acc_diff_roll']])
    #     dat['acc_range']=dat['acc_range']*100

    dat['green_recovery'] = 100 - abs(dat['green_range'] - green_base) * 100
    dat['Red_recovery'] = 100 - abs(dat['Red_range'] - Red_base) * 100
    dat['IR_recovery'] = 100 - abs(dat['IR_range'] - IR_base) * 100
    dat.fillna(method="ffill", inplace=True)

    #Add saturation values
    dat['IR_O'] = (max(dat['IR']) - min(dat['IR']))/dat['IR']#.mean()
    dat['Red_O'] = (max(dat['Red']) - min(dat['Red'])) / dat['Red']#.mean()
    dat['Red_IR_O'] = dat['Red_O']/10/dat['IR_O']
    dat['saturation'] = 100-(25 * dat['Red_IR_O'])
    dat.fillna(method="ffill", inplace=True)
    # print(dat)
    # print(dat.columns)
    return dat
