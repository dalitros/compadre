import pandas as pd
import numpy as np
from constants import *
import logging
import boto3
import io
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def summarize(dat=pd.DataFrame()):
    if dat.empty:
        raise ValueError('DataFrame is empty')
    dat = dat.bfill()
    acc_range = dat['acc_range'].mean()
    logger.exception("Columns in Summarize: %s", dat.columns)
    temperature = dat['Temp'].mean()
    hr = round((dat['0'].mean()), 4)
    # hr = 60
    intensity = round((hr * 100 / 220), 1)

    rehab = round(
        (100 - abs(dat['green_recovery'].mean() - dat['IR_recovery'].mean())), 4)
    if rehab < 5000:
        sizes = [100 - abs(dat['green_recovery'].mean() - dat['IR_recovery'].mean()),
                 abs(dat['green_recovery'].mean() - dat['IR_recovery'].mean())]
    # r1 parameter calculation
    dat["ir_green_range_ratio_rol"] = dat["ir_green_range_ratio"].mean()
    condition = dat['ir_green_range_ratio_rol'] > 1
    # dat['ir_green_range_ratio_rol_norm1'] = np.where(condition, ((dat['ir_green_range_ratio_rol'] - 1) / 9) * 100,
    #                                                  ((dat['ir_green_range_ratio_rol'] + 1)/9 * 100))
    dat['ir_green_range_ratio_rol_norm1'] = np.where(condition,
                                                     (dat['ir_green_range_ratio_rol'] + 1) / 9 * 10,
                                                     dat['ir_green_range_ratio_rol'] * 10)

    r1 = abs(dat['ir_green_range_ratio_rol_norm1'].mean())
    if r1 < 0:
        r1 = 0
    elif r1 > 99:
        r1 = 100
    elif np.isnan(r1):  # Skip the update if size is NaN
        r1 = 0
    else:
        r1 = r1
    dat = dat.fillna(method="bfill")
    dat = dat[~(dat.isin([np.inf, -np.inf]).any(axis=1))]

    # r2 parameter calculation
    dat["red_ir_ratio_rol"] = dat["red_ir_range_ratio"].mean()
    condition = dat['red_ir_ratio_rol'] > 1
    # dat['red_ir_ratio_rol_norm1'] = np.where(condition, ((dat['red_ir_ratio_rol'] - 1) / 9) * 10,
    #                                          ((dat['red_ir_ratio_rol'] + 1 / 9) * 10))
    dat['red_ir_ratio_rol_norm1'] = np.where(condition, (dat['red_ir_ratio_rol'] + 1) / 9 * 10,
                                             dat['red_ir_ratio_rol'] * 10)

    dat = dat.fillna(method="bfill")
    dat = dat[~(dat.isin([np.inf, -np.inf]).any(axis=1))]
    # r2 = abs(dat1['red_ir_range_ratio_rol_norm1'].mean())
    r2 = abs(dat['red_ir_ratio_rol_norm1'].mean())
    if r2 < 0:
        r2 = 0
    elif r2 > 99:
        r2 = 100
    elif np.isnan(r2):  # Skip the update if size is NaN
        r2 = 0
    else:
        r2 = r2
    # r3 parameter calculation
    dat["red_green_ratio_rol"] = dat["red_green_range_ratio"]
    condition = dat['red_green_ratio_rol'] > 1
    dat['red_green_ratio_rol_norm1'] = np.where(condition, (dat['red_green_ratio_rol'] * 10),
                                                dat['red_green_ratio_rol'] * 10)
    dat = dat.fillna(method="bfill")
    dat = dat[~(dat.isin([np.inf, -np.inf]).any(axis=1))]
    r3 = abs(dat['red_green_ratio_rol_norm1'].mean())
    if r3 < 0:
        r3 = 0
    elif r3 > 99:
        r3 = 100
    else:
        r3 = r3

    # r4 parameter calculation
    r4 = (abs(dat['green_recovery'].mean() - dat['IR_recovery'].mean())) * 10
    if r4 < 0:
        r4 = 0
    elif r4 > 99:
        r4 = 100
    else:
        r4 = r4
    # r4 = 100-rehab
    print(r1, r2, r3,r4)
    r = (r1 + r3 + r2 + r4) / 4

    risk_of_injury = round(abs(r), 4) if not np.isnan(r) else r3
    if risk_of_injury < 0:
        risk_of_injury = 0
    elif risk_of_injury > 100:
        risk_of_injury = 100
    # else:
    #     risk_of_injury = risk_of_injury
    # risk_of_injury = round(
    #     ((r1 + r2 + r3 + r4)/4), 4) if not np.isnan(r1 + r2 + r3) else r3

    t = (temperature - 25) * 100 / (35 - 25)
    m = acc_range
    h = (hr - 50) * 100 / (200 - 50)
    # h = (hr - 60) * 100 / (200 - 60)
    warm_up = round((h + m + t)/ 2, 4)
    # warm_up = 50
    # round(((h + m + t) / 2), 4)

    if dat['Red'].mean() >= 30000:
        body_connection = 1
    else:
        body_connection = 0
        
    #################################################################################################### Upload to S3

    #################################################################################################################33
    return print(
        'RISK_OF_INJURY:', risk_of_injury,
        'WARMP_UP:', warm_up,
        'INTENSITY:', intensity,
        'RECOVERY:', rehab,
        'BODY_CONNECTION:', body_connection)


csv_path = 'C:/Users/dalit/Documents/gainguard/data/log_ppg/cal_exp/Tamir/160124/all.csv'
dat = pd.read_csv(csv_path)
summarize(dat=dat)