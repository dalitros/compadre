import numpy as np
import pandas as pd
from .decompose1 import decompos_signal#,decompos_signal1
from sklearn.preprocessing import MinMaxScaler
from .predict_HR1 import prediction_xgbr

"""
This script engineer and add new features, calculated by functions, algorithms and models into output csv. 
Any new feature should be added at the end of the script above the return function.
The output new csv will be called by the pipline function.
"""

# For 300 lines analysis.
def feature_eng (dat):#,file_name=None):#,signal=None):
    # dat = pd.read_csv(file)
    # New Features based on data

    signals=['IR','Red','green']
    for signal in signals:
        seas_decomp, dat = decompos_signal(df=dat, signal=signal)


    dat = dat.fillna(method="bfill")
    # dat = table
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
    dat['vec_acc'] = np.sqrt((dat['Ax'] ** 2) + (dat['Ay'] ** 2) + (dat['Az'] ** 2))  ##(meters)
    dat['vec_g'] = np.sqrt((dat['Gx'] ** 2) + (dat['Gy'] ** 2) + (dat['Gz'] ** 2))  ##(meters)
    dat['vec_acc_diff'] = dat['vec_acc'].diff()
    dat['vec_g_diff'] = dat['vec_g'].diff()
    dat = dat[~(dat.isnull().any(axis=1))]  # to remove nan
    dat = dat[~(dat.isin([np.inf, -np.inf]).any(axis=1))]  # to remove inf
    dat = dat.reset_index(drop=True)

    # Predict
    model_path = 'C:/workspace/Machine_learning/server/api/my_package_for_ble/acc15.json'
    y_pred = prediction_xgbr(dat,model_path)
    pr_table = pd.concat([dat, y_pred], axis=1)
    dat = pr_table

    # Other feature engineering
    scaler = MinMaxScaler(feature_range=(0, 1))
    dat['vec_g_roll'] = dat['vec_g'].rolling(10).mean()
    dat['Tilt_range'] = dat['vec_g_roll'] * 100 / 2000
    dat['zeros'] = 0

    dat['green_trend1'] = dat['green_trend']
    dat['Red_trend1'] = dat['Red_trend']
    dat['IR_trend1'] = dat['IR_trend']
    dat['green_trend1'] = dat['green_trend1'].fillna(dat['green'])  # , inplace=True)
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
    dat['movement1'] = np.where((dat['vec_acc_diff'] >= 1000) | (dat['vec_acc_diff'] <= -1000), 1, 0)
    dat['movement2'] = np.where((dat['vec_acc_diff'] >= 110) | (dat['vec_acc_diff'] <= -110), 1, 0)
    dat['tilt1'] = np.where((dat['vec_g_diff'] > 200) | (dat['vec_g_diff'] < -200), 1, 0)
    dat['tilt2'] = np.where((dat['vec_g_diff'] > 100) | (dat['vec_g_diff'] < -100), 1, 0)
    dat['vec_acc_diff_roll'] = abs(dat['vec_acc_diff']).rolling(10).mean()

    scaler = MinMaxScaler(feature_range=(0, 1))
    dat['acc_range'] = dat['vec_acc_diff_roll'] * 100 / 20000
    #     dat['acc_range'] = scaler.fit_transform(dat[['vec_acc_diff_roll']])
    #     dat['acc_range']=dat['acc_range']*100

    dat['green_recovery'] = 100 - abs(dat['green_range'] - green_base) * 100
    dat['Red_recovery'] = 100 - abs(dat['Red_range'] - Red_base) * 100
    dat['IR_recovery'] = 100 - abs(dat['IR_range'] - IR_base) * 100
    dat.fillna(method="ffill", inplace=True)
    # print(dat)
    # print(dat.columns)
    return dat

    # For less than 300 lines analysis.
def feature_eng1(dat):
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
    dat['vec_acc'] = np.sqrt((dat['Ax'] ** 2) + (dat['Ay'] ** 2) + (dat['Az'] ** 2))  ##(meters)
    dat['vec_g'] = np.sqrt((dat['Gx'] ** 2) + (dat['Gy'] ** 2) + (dat['Gz'] ** 2))  ##(meters)
    dat['vec_acc_diff'] = dat['vec_acc'].diff()
    dat['vec_g_diff'] = dat['vec_g'].diff()

    scaler = MinMaxScaler(feature_range=(0, 1))
    dat['vec_g_roll'] = dat['vec_g'].mean()
    dat['Tilt_range'] = dat['vec_g_roll'] * 100 / 2000
    dat['zeros'] = 0

    dat['green_range'] = scaler.fit_transform(dat[['green']])
    dat['Red_range'] = scaler.fit_transform(dat[['Red']])
    dat['IR_range'] = scaler.fit_transform(dat[['IR']])
    green_base = dat['green_range'][0:10].mean()
    Red_base = dat['Red_range'][0:10].mean()
    IR_base = dat['IR_range'][0:10].mean()

    dat['red_ir_range_ratio'] = dat['Red_range'] / dat['IR_range']
    dat['red_green_range_ratio'] = dat['Red_range'] / dat['green_range']
    dat['ir_green_range_ratio'] = dat['IR_range'] / dat['green_range']

    dat['red_ir_ratio'] = dat['Red'] / dat['IR']
    dat['red_green_ratio'] = dat['Red'] / dat['green']
    dat['ir_green_ratio'] = dat['IR'] / dat['green']
    dat['movement1'] = np.where((dat['vec_acc_diff'] >= 1000) | (dat['vec_acc_diff'] <= -1000), 1, 0)
    dat['movement2'] = np.where((dat['vec_acc_diff'] >= 110) | (dat['vec_acc_diff'] <= -110), 1, 0)
    dat['tilt1'] = np.where((dat['vec_g_diff'] > 200) | (dat['vec_g_diff'] < -200), 1, 0)
    dat['tilt2'] = np.where((dat['vec_g_diff'] > 100) | (dat['vec_g_diff'] < -100), 1, 0)
    dat['vec_acc_diff_roll'] = abs(dat['vec_acc_diff']).mean()

    scaler = MinMaxScaler(feature_range=(0, 1))
    dat['acc_range'] = dat['vec_acc_diff_roll'] * 100 / 20000

    dat['green_recovery'] = 100 - abs(dat['green_range'] - green_base) * 100
    dat['Red_recovery'] = 100 - abs(dat['Red_range'] - Red_base) * 100
    dat['IR_recovery'] = 100 - abs(dat['IR_range'] - IR_base) * 100
    dat.fillna(method="ffill", inplace=True)

    return dat
    # Can add here more outputs using other models or algorithms

# Example
# signal='IR'
# file='C:/Users/dalit/Documents/gainguard/data/log_ppg/cal_exp/Tamir/300423/Tricep_Left_Rest_resting_0_data.csv'
# # # file_name="~/Documents/gainguard/data/log_ppg/cal_exp/Tamir/2023-04-11_13-06-01_log_ana.csv"
# dat=pd.read_csv(file)
# feature_eng (dat)
