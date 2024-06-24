# import os
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# SessionData: {
#   userId: string;
#   muscleName: string;
#   areaName: string;
#   gyroValues?: number[];
#   accelValues?: number[];
#   emgValues?: number[];
#   emg?: number;
#   irValues?: number[];
#   temperature?: number;
#   timestamp: number;
# }
# data: SessionData[]

# sample entry:
# {'accelValues': {'L': [{'N': '3904'}, {'N': '-12612'}, {'N': '-9256'}]}, 'emgValues': {'L': []}, 'userId': {'S': 'default_user'}, 'timestamp': {'N': '1695671912513'}, 'connectionId': {'S': 'L1Dq0e9OIAMAbSg='}, 'areaName': {'S': 'areaNamePlaceholder'}, 'irValues': {'L': []}, 'muscleName': {'S': 'rightThigh'}, 'temperature': {'N': '31'}, 'gyroValues': {'L': [{'N': '-288'}, {'N': '279'}, {'N': '-49'}]}}

def convert_session_data_list_to_dataframe(data):
    logger.info("convert_session_data_list_to_csv_300_lines")
    df = pd.DataFrame(data)
    logger.info("header: {}".format(df.columns))
    logger.info("number of lines: {}".format(len(df)))
    df.drop(['connectionId'], axis=1, inplace=True)
    # df.drop(['userId'], axis=1, inplace=True)
    df.drop(['areaName'], axis=1, inplace=True)
    # df.drop(['muscleName'], axis=1, inplace=True)

    if 'userId' in df.columns:
        df['userId'] = df['userId'].apply(lambda x: x['S'] if isinstance(x, dict) and 'S' in x else np.nan)
    if 'userId' in df.columns:
        df['muscleName'] = df['muscleName'].apply(lambda x: x['S'] if isinstance(x, dict) and 'S' in x else np.nan)
    if 'emgValues' in df.columns:
        df['EMG'] = df['emgValues'].apply(lambda x: float(
            x['L'][0]['N']) if isinstance(x, dict) and len(x['L']) > 0 else np.nan)
        df.drop(['emgValues'], axis=1, inplace=True)
    if 'emg' in df.columns:
        df['EMG'] = df['emg'].apply(lambda x: float(
            x['N']) if isinstance(x, dict) else np.nan)
        df.drop(['emg'], axis=1, inplace=True)
    if 'temperature' in df.columns:
        df['Temp'] = df['temperature'].apply(
            lambda x: float(x['N']) if isinstance(x, dict) else np.nan)
        df.drop(['temperature'], axis=1, inplace=True)

    if 'gyroValues' in df.columns:
        df['Gx'] = df['gyroValues'].apply(lambda x: float(
            x['L'][0]['N']) if isinstance(x, dict) and len(x['L']) > 0 else np.nan)
        df['Gy'] = df['gyroValues'].apply(lambda x: float(
            x['L'][1]['N']) if isinstance(x, dict) and len(x['L']) > 1 else np.nan)
        df['Gz'] = df['gyroValues'].apply(lambda x: float(
            x['L'][2]['N']) if isinstance(x, dict) and len(x['L']) > 2 else np.nan)
        df.drop(['gyroValues'], axis=1, inplace=True)

    if 'accelValues' in df.columns:
        df['Ax'] = df['accelValues'].apply(lambda x: float(
            x['L'][0]['N']) if isinstance(x, dict) and len(x['L']) > 0 else np.nan)
        df['Ay'] = df['accelValues'].apply(lambda x: float(
            x['L'][1]['N']) if isinstance(x, dict) and len(x['L']) > 1 else np.nan)
        df['Az'] = df['accelValues'].apply(lambda x: float(
            x['L'][2]['N']) if isinstance(x, dict) and len(x['L']) > 2 else np.nan)
        df.drop(['accelValues'], axis=1, inplace=True)

    if 'irValues' in df.columns:
        df['IR'] = df['irValues'].apply(lambda x: float(
            x['L'][0]['N']) if isinstance(x, dict) and len(x['L']) > 0 else np.nan)
        df['Red'] = df['irValues'].apply(lambda x: float(
            x['L'][1]['N']) if isinstance(x, dict) and len(x['L']) > 1 else np.nan)
        df['green'] = df['irValues'].apply(lambda x: float(
            x['L'][2]['N']) if isinstance(x, dict) and len(x['L']) > 2 else np.nan)
        df.drop(['irValues'], axis=1, inplace=True)

    if 'timestamp' in df.columns:
        df['timestamp'] = df['timestamp'].apply(
            lambda x: int(x['N']) if isinstance(x, dict) else np.nan)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        # Convert the 'datetime' column to datetime objects
        df['datetime'] = pd.to_datetime(
            df['datetime'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
        # Create a new column 'time_round' with the formatted time (milliseconds rounded)
        df['time_round'] = df['datetime'].dt.strftime('%H:%M:%S.%f').str[:-5]
        df.drop(['timestamp'], axis=1, inplace=True)
       # Identify non-numeric columns
        non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
        # Separate non-numeric columns
        non_numeric_data = df[non_numeric_columns]
        # Convert object columns to numeric data types
        numeric_columns = df.columns.difference(non_numeric_columns)
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        # Handle missing values
        df.dropna(inplace=True)

    logger.info("transformed header: {}".format(df.columns))
    logger.info("transformed first 10 lines: {}".format(df.head(10)))
    # result = df.groupby('time_round').mean().reset_index()
    mean_data = df.groupby('time_round')[numeric_columns].mean().reset_index()
    result = pd.merge(mean_data, non_numeric_data, on='time_round', how='left')
    # for column in result:
    #     # Use linear interpolation to impute missing values
    #     result[column] = result[column].interpolate()
    #     result = result.fillna(method="bfill")
    #     # print(result)
    ###############################################################################################
    # logger.info("convert_session_data_list_to_csv_300_lines: {}".format(result))
    return result
