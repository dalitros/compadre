# import os
import re
import numpy as np
import pandas as pd
import json
"""
This script convert log/ble .txt output into csv.
To convert json to csv, other script should be made. 
"""
def read_last_lines(file_path, num_lines):
    # Read the last 'num_lines' lines from a file
    lines = []
    data = pd.read_json(file_path, lines=True, nrows=num_lines)
    # Create an empty DataFrame
    return data

# For 300 lines analysis.
def from_json_to_csv(dirs):

    # Read the last saved lines
    data = read_last_lines(dirs, 300)
    print(data)
    df = pd.DataFrame(data)
    dfs = []
    if 'emgValues' in data:
        df['EMG'] = data['emgValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)

    if 'temperature' in data:
        df['Temp'] = data['temperature']
    # Divide 'gyroValues' into separate columns if it exists 'Gx', 'Gy','Gz'
    #     if 'gyroValues' in data:
    #         df['Gx'] = data['gyroValues']
    #               # Divide 'gyroValues' into separate columns if it exists
    if 'gyroValues' in data:
        df['Gx'] = data['gyroValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)
        df['Gy'] = data['gyroValues'].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else np.nan)
        df['Gz'] = data['gyroValues'].apply(lambda x: x[2] if isinstance(x, list) and len(x) > 2 else np.nan)

    # Divide 'accelValues' into separate columns if it exists
    if 'accelValues' in data:
        df['Ax'] = data['accelValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)
        df['Ay'] = data['accelValues'].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else np.nan)
        df['Az'] = data['accelValues'].apply(lambda x: x[2] if isinstance(x, list) and len(x) > 2 else np.nan)

    # Divide 'irValues' into separate columns if it exists
    if 'irValues' in data:
        df['IR'] = data['irValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)
        df['Red'] = data['irValues'].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else np.nan)
        df['green'] = data['irValues'].apply(lambda x: x[2] if isinstance(x, list) and len(x) > 2 else np.nan)

    # Convert 'timestamp' to a datetime object and format it
    if 'timestamp' in data:
        df['datetime'] = pd.to_datetime(data['timestamp'], unit='ms', utc=True)
        # Convert the 'datetime' column to datetime objects
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
        # Create a new column 'time_round' with the formatted time (milliseconds rounded)
        df['time_round'] = df['datetime'].dt.strftime('%H:%M:%S.%f').str[:-5]

        # Append the DataFrame to the list
        dfs.append(df)

    # Combine all DataFrames from different JSON objects into one DataFrame
    result_df = pd.concat(dfs, ignore_index=True)
    table = result_df[['datetime', 'time_round', 'Temp', 'EMG', 'IR', 'Red', 'green',
                       'Gx', 'Gy', 'Gz', 'Ax', 'Ay', 'Az']]
    dat = table.groupby('time_round').mean().reset_index()
    for column in dat:
        # Use linear interpolation to impute missing values
        dat[column] = dat[column].interpolate()
        dat = dat.fillna(method="bfill")
        print(dat)
    ###############################################################################################

    return dat

# For less than 300 lines analysis.
def from_json_to_csv1(dirs):
    # Read the last saved lines
    data = read_last_lines(dirs, 50)
    df = pd.DataFrame(data)
    dfs = []
    if 'emgValues' in data:
        df['EMG'] = data['emgValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)

    if 'temperature' in data:
        df['Temp'] = data['temperature']
    # Divide 'gyroValues' into separate columns if it exists 'Gx', 'Gy','Gz'
    #     if 'gyroValues' in data:
    #         df['Gx'] = data['gyroValues']
    #               # Divide 'gyroValues' into separate columns if it exists
    if 'gyroValues' in data:
        df['Gx'] = data['gyroValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)
        df['Gy'] = data['gyroValues'].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else np.nan)
        df['Gz'] = data['gyroValues'].apply(lambda x: x[2] if isinstance(x, list) and len(x) > 2 else np.nan)

    # Divide 'accelValues' into separate columns if it exists
    if 'accelValues' in data:
        df['Ax'] = data['accelValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)
        df['Ay'] = data['accelValues'].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else np.nan)
        df['Az'] = data['accelValues'].apply(lambda x: x[2] if isinstance(x, list) and len(x) > 2 else np.nan)

    # Divide 'irValues' into separate columns if it exists
    if 'irValues' in data:
        df['IR'] = data['irValues'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan)
        df['Red'] = data['irValues'].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else np.nan)
        df['green'] = data['irValues'].apply(lambda x: x[2] if isinstance(x, list) and len(x) > 2 else np.nan)

    # Convert 'timestamp' to a datetime object and format it
    if 'timestamp' in data:
        df['datetime'] = pd.to_datetime(data['timestamp'], unit='ms', utc=True)
        # Convert the 'datetime' column to datetime objects
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
        # Create a new column 'time_round' with the formatted time (milliseconds rounded)
        df['time_round'] = df['datetime'].dt.strftime('%H:%M:%S.%f').str[:-5]

        # Append the DataFrame to the list
        dfs.append(df)

    # Combine all DataFrames from different JSON objects into one DataFrame
    result_df = pd.concat(dfs, ignore_index=True)
    table = result_df[['datetime', 'time_round', 'Temp', 'EMG', 'IR', 'Red', 'green',
                       'Gx', 'Gy', 'Gz', 'Ax', 'Ay', 'Az']]
    dat = table.groupby('time_round').mean().reset_index()
    for column in dat:
        # Use linear interpolation to impute missing values
        dat[column] = dat[column].interpolate()
        dat = dat.fillna(method="bfill")
    #     print(dat)
    ###############################################################################################
    return dat

# Example

# dirs = "C:/Users/logger/Patients/2023_08_28output.txt"
# # # dirs = "C:/Users/logger/Patients/2023_07_31output.txt"
# # # # file_name = "Forearm_Right_Rest_Sitting_0_data.csv"
# from_logger_to_csv1(dirs)
