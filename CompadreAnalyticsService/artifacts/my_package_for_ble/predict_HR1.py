import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler

"""
This function call data features in dataframe format and predict heart rate. To more accurate prediction, a new model
should be trained.
"""
model_path = "Machine_learning/server/api/my_package_for_ble/acc15.json"
# model_path=locs+"\acc9.json"

# def main():
def input_prep(dat):
    features=[
        'Ax', 'Ay', 'Az',
        'green',
        'acc_x_diff', 'acc_y_diff', 'acc_z_diff',
        'vec_acc_diff', 'vec_acc',
        'ppg_season_40', 'ppg_season_50', 'ppg_season_60', 'ppg_season_70', 'ppg_season_80',
              ]
    X_train=dat[features]

    scaler = MinMaxScaler(feature_range=(0, 1))
    X_train = scaler.fit_transform(X_train)
    X_train=pd.DataFrame(X_train,columns=[
        'Ax', 'Ay', 'Az',
        'green',
        'acc_x_diff', 'acc_y_diff', 'acc_z_diff',
        'vec_acc_diff', 'vec_acc',
        'ppg_season_40', 'ppg_season_50', 'ppg_season_60', 'ppg_season_70', 'ppg_season_80',
    ])
    return X_train

def prediction_xgbr(dat,model_path):
    X_train=input_prep(dat)
    global XGBR1
    XGBR1 = xgb.XGBRegressor()
    XGBR1.load_model(model_path)
    y_pred_tr = XGBR1.predict(X_train)
    y_pred=pd.DataFrame(np.round(y_pred_tr))#.reset_index(inplace = True)
    # print(y_pred)
    return y_pred
