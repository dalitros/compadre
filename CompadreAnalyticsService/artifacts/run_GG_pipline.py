# import requests
from my_package_for_ble.ppg_imu_from_logger1 import from_logger_to_csv,from_logger_to_csv1
# from django.http import JsonResponse
from my_package_for_ble.feat_eng1 import feature_eng, feature_eng1
from my_package_for_ble.ppg_imu_from_ble_json import from_json_to_csv,from_json_to_csv1
import time
import numpy as np
import os
# from .my_package.upload_to_s3 import csv_to_s3


path = "C:/Users/logger/Patients/"


class Body_connection:
    pass

def run_dev():
    #1. Making path to log file. Instead you can use the url link.
    path = "C:/Users/logger/Patients/"
    try:
        os.mkdir(path)
    except:
        pass
    curr_time = time.strftime('%Y_%m_%d', time.localtime())
    # path = "C:/Users/dalit/Documents/gainguard/data/log_ppg/logger/Patients/"
    path = "C:/Users/logger/Patients/"
    dirs = path + str(curr_time) + 'output.txt'
    #json file fot testing
    # dirs = "C:/Users/dalit/Documents/gainguard/data/log_ppg/logger/rightUpperArm.json"
#***************************************************************************************
    # 2. For .txt files - calling ble/log data from server.
    try:
        data = from_logger_to_csv(dirs)  # Import data from logger and convert to csv
        data1 = from_logger_to_csv1(dirs)
        print('txt log')
    # 2. For .json files - calling ble/log data from server.
    except:
        data = from_json_to_csv(dirs)  # Import data from logger and convert to csv
        data1 = from_json_to_csv1(dirs)
        print('json log')

#**************************************************************************************
    # 2. Analyse and add Features
    dat = feature_eng(data)
    dat1 = feature_eng1(data1)

# **************************************************************************************
    # 3. Upload_to_s3
    # csv_to_s3(data)

# **************************************************************************************
    # 4. Uploading new feature/output as json to url
    acc_range = dat['acc_range'].mean()
    Temp = dat['Temp'].mean()
    hr = round((dat[0].mean()), 4)
    intensity = round((hr * 100 / 220), 1)

    rehab = round((100 - abs(dat1['green_recovery'].mean() - dat1['IR_recovery'].mean())), 4)
    # r1 parameter calculation
    dat1["ir_green_range_ratio_rol"] = dat1["ir_green_range_ratio"].mean()
    condition = dat1['ir_green_range_ratio_rol'] > 1
    dat1['ir_green_range_ratio_rol_norm1'] = np.where(condition, ((dat1['ir_green_range_ratio_rol'] - 1) / 9) * 100,
                                                     ((dat1['ir_green_range_ratio_rol'] + 1)/9 * 100))

    r1 = abs(dat1['ir_green_range_ratio_rol_norm1'].mean())
    if r1 < 0:
        r1 = 0
    elif r1 > 99:
        r1 = 10
    elif np.isnan(r1):  # Skip the update if size is NaN
        r1 = 0
    else:
        r1 = r1
    dat1 = dat1.fillna(method="bfill")
    dat1 = dat1[~(dat1.isin([np.inf, -np.inf]).any(axis=1))]

    # r2 parameter calculation
    dat1["red_ir_ratio_rol"] = dat1["red_ir_ratio"].mean()
    condition = dat1['red_ir_ratio_rol'] > 1
    dat1['red_ir_ratio_rol_norm1'] = np.where(condition, ((dat1['red_ir_ratio_rol'] - 1) / 9) * 10,
                                             ((dat1['red_ir_ratio_rol'] + 1 / 9) * 10))

    dat1 = dat1.fillna(method="bfill")
    dat1 = dat1[~(dat1.isin([np.inf, -np.inf]).any(axis=1))]
    # r2 = abs(dat1['red_ir_range_ratio_rol_norm1'].mean())
    r2 = abs(dat1['red_ir_ratio_rol_norm1'].mean())
    if r2 < 0:
        r2 = 0
    elif r2 > 99:
        r2 = 10
    elif np.isnan(r2):  # Skip the update if size is NaN
        r2 = 0
    else:
        r2 = r2
    r3 = 100-rehab
    print(r1,r2,r3)
    # r=[r1 + r2 + r3]

    risk_of_injury = round(((r1 + r2 + r3)/3),4) if not np.isnan(r1 + r2 + r3) else r3

    t = (Temp - min(dat['Temp'])) * 100 / (35 - 25)
    m = acc_range
    h = (hr - min(dat[0])) * 100 / (200 - min(dat[0]))
    # warm_up = round(((h + m + t) / 3), 4)
    warm_up = round(((h + m + t) / 2), 4)

    if dat1['Red'].mean() >= 30000:
        Body_connection = 1
    else:
        Body_connection = 0

    print ({'Intensity': intensity, 'Recovery': rehab, 'Risk_of_injury': risk_of_injury, 'Warm_up': warm_up,
     'Body_connection': Body_connection})
    return (
        {'Intensity': intensity, 'Recovery': rehab, 'Risk_of_injury': risk_of_injury, 'Warm_up': warm_up,
         'Body_connection': Body_connection})

if __name__ == "__main__":
    run_dev()