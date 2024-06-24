import os
import re
import numpy as np
import pandas as pd
"""
This script convert log/ble .txt output into csv.
To convert json to csv, other script should be made. 
"""
def read_last_lines(file_path, num_lines):
    # Read the last 'num_lines' lines from a file
    lines = []
    with open(file_path, 'r', encoding='cp1252') as file:
        for line in file:
            lines.append(line.strip())
            if len(lines) > num_lines:
                lines.pop(0)
    return lines

# For 300 lines analysis.
def from_logger_to_csv(dirs):

    # Read the last saved lines
    lines=read_last_lines(dirs, 300)
    print(lines)
#     with open(dirs, 'r') as file:
#         lines = file.readlines()

    # Define a regular expression pattern to extract the timestamp, tag, and message from each line
    pattern = r'\[(\d{2}:\d{2}:\d{2}.\d{3}),\s*(\w+)\]\s+(.*)'
    # Create empty lists to store the extracted data
    timestamps = []
    tags = []
    messages = []

    # Iterate over each line, extract the data, and append it to the lists
    for line in lines:
        match = re.search(pattern, line)
        print(match)
        if match:
            timestamps.append(match.group(1))
            tags.append(match.group(2))
            messages.append(match.group(3))

    # Create a pandas DataFrame from the extracted data
    time = pd.DataFrame({'timestamp': timestamps, 'tag': tags, 'message': messages})
    print(time)
    # def create_table(df_time):
    df_time = time[0:len(time)]
    df_time = df_time.reset_index(drop=True)
    # convert the 'datetime' column to a datetime object
    df_time['datetime'] = pd.to_datetime(df_time['timestamp'])
    # format the 'datetime' column as a string with milliseconds
    df_time['datetime'] = df_time['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    # Read the log file into a Pandas DataFrame
    # df = pd.read_csv(dirs, delimiter='\t')
    df = df_time

    # Define regular expressions to extract data from each string
    ir_regex = re.compile(r"IR: (\d+)")
    red_regex = re.compile(r"Red: (\d+)")
    green_regex = re.compile(r"green: (\d+)")
    Gx_regex = re.compile(r"Gx: (-?\d+)")
    Gy_regex = re.compile(r"Gy: (-?\d+)")
    Gz_regex = re.compile(r"Gz: (-?\d+)")
    Ax_regex = re.compile(r"Ax: (-?\d+)")
    Ay_regex = re.compile(r"Ay: (-?\d+)")
    Az_regex = re.compile(r"Az: (-?\d+)")
    Temp_regex = re.compile(r"Temp: (\d+)")
    EMG_regex = re.compile(r"EMG[0]: (\d+)")

    # Iterate over each string and extract relevant data using regular expressions
    PPG = []
    for index, row in df.iterrows():
        ir_match = ir_regex.search(row['message'])
        red_match = red_regex.search(row['message'])
        green_match = green_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}

        if ir_match:
            parsed_data['IR'] = int(ir_match.group(1))
        if red_match:
            parsed_data['Red'] = int(red_match.group(1))
        if green_match:
            parsed_data['green'] = int(green_match.group(1))
        PPG.append(parsed_data)

    PPG_params = pd.DataFrame(PPG)
    PPGtable = PPG_params.dropna(subset=['IR', 'Red', 'green'], how='all', axis=0)
    PPGtable = PPGtable.reset_index(drop=True)
    PPGtable['datetime'] = pd.to_datetime(PPGtable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    PPGtable['time_round'] = PPGtable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    gyro = []
    for index, row in df.iterrows():
        Gx_match = Gx_regex.search(row['message'])
        Gy_match = Gy_regex.search(row['message'])
        Gz_match = Gz_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}
        if Gx_match:
            parsed_data['Gx'] = int(Gx_match.group(1))
        if Gy_match:
            parsed_data['Gy'] = int(Gy_match.group(1))
        if Gz_match:
            parsed_data['Gz'] = int(Gz_match.group(1))
        gyro.append(parsed_data)

    gyro_params = pd.DataFrame(gyro)
    gyrotable = gyro_params.dropna(subset=['Gx', 'Gy', 'Gz'], how='all', axis=0)
    gyrotable = gyrotable.reset_index(drop=True)
    gyrotable['datetime'] = pd.to_datetime(gyrotable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    gyrotable['time_round'] = gyrotable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    acc = []
    for index, row in df.iterrows():
        Ax_match = Ax_regex.search(row['message'])
        Ay_match = Ay_regex.search(row['message'])
        Az_match = Az_regex.search(row['message'])
        # Temp_match = Temp_regex.search(row['message'])
        # EMG_match = EMG_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}
        if Ax_match:
            parsed_data['Ax'] = int(Ax_match.group(1))
        if Ay_match:
            parsed_data['Ay'] = int(Ay_match.group(1))
        if Az_match:
            parsed_data['Az'] = int(Az_match.group(1))
        acc.append(parsed_data)

    acc_params = pd.DataFrame(acc)
    acctable = acc_params.dropna(subset=['Ax', 'Ay', 'Az'], how='all', axis=0)
    acctable = acctable.reset_index(drop=True)
    acctable['datetime'] = pd.to_datetime(acctable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    acctable['time_round'] = acctable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    # try:
    emg_tmp = []
    for index, row in df.iterrows():
        Temp_match = Temp_regex.search(row['message'])
        EMG_match = EMG_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}
        if Temp_match:
            parsed_data['Temp'] = int(Temp_match.group(1))
        if EMG_match:
            parsed_data['EMG'] = int(EMG_match.group(1))
        emg_tmp.append(parsed_data)

    emg_tmptable = pd.DataFrame(emg_tmp)
    emg_tmptable = emg_tmptable.dropna(subset=['Temp'], how='all', axis=0)
    emg_tmptable = emg_tmptable.reset_index(drop=True)
    emg_tmptable['datetime'] = pd.to_datetime(emg_tmptable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    emg_tmptable['time_round'] = emg_tmptable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    imu = pd.merge(gyrotable, acctable, on="time_round", how="inner")
    print("imu",imu)
    ppg = pd.merge(PPGtable, imu, on="time_round", how="inner")
    print("ppg",ppg)

    table = pd.merge(emg_tmptable, ppg, on="time_round", how="inner",suffixes=('time_round', 'time_round'))
    print("table", table)

    table = table.sort_index(axis=0, ascending=True).reset_index(inplace=False, drop=True)
    table = table.dropna()
    table = table.reset_index(drop=True)
    dat = table

    dat = dat[~(dat.isnull().any(axis=1))]  # remove nan
    dat = dat[~(dat.isin([np.inf, -np.inf]).any(axis=1))]  # remove inf
    dat = dat.reset_index(drop=True)
    print(dat.columns)
    ###############################################################################################

    print(emg_tmptable)

    return dat

# For less than 300 lines analysis.
def from_logger_to_csv1(dirs):
    # Read the last saved lines
    lines = read_last_lines(dirs, 50)
    # Define a regular expression pattern to extract the timestamp, tag, and message from each line
    pattern = r'\[(\d{2}:\d{2}:\d{2}.\d{3}),\s*(\w+)\]\s+(.*)'
    # Create empty lists to store the extracted data
    timestamps = []
    tags = []
    messages = []

    # Iterate over each line, extract the data, and append it to the lists
    for line in lines:
        match = re.search(pattern, line)
        if match:
            timestamps.append(match.group(1))
            tags.append(match.group(2))
            messages.append(match.group(3))

    # Create a pandas DataFrame from the extracted data
    time = pd.DataFrame({'timestamp': timestamps, 'tag': tags, 'message': messages})

    # def create_table(df_time):
    df_time = time[0:len(time)]
    df_time = df_time.reset_index(drop=True)
    # convert the 'datetime' column to a datetime object
    df_time['datetime'] = pd.to_datetime(df_time['timestamp'])
    # format the 'datetime' column as a string with milliseconds
    df_time['datetime'] = df_time['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    # Read the log file into a Pandas DataFrame
    # df = pd.read_csv(dirs, delimiter='\t')
    df = df_time

    # Define regular expressions to extract data from each string
    ir_regex = re.compile(r"IR: (\d+)")
    red_regex = re.compile(r"Red: (\d+)")
    green_regex = re.compile(r"green: (\d+)")
    Gx_regex = re.compile(r"Gx: (-?\d+)")
    Gy_regex = re.compile(r"Gy: (-?\d+)")
    Gz_regex = re.compile(r"Gz: (-?\d+)")
    Ax_regex = re.compile(r"Ax: (-?\d+)")
    Ay_regex = re.compile(r"Ay: (-?\d+)")
    Az_regex = re.compile(r"Az: (-?\d+)")
    Temp_regex = re.compile(r"Temp: (\d+)")
    EMG_regex = re.compile(r"EMG[0]: (\d+)")

    # Iterate over each string and extract relevant data using regular expressions
    PPG = []
    for index, row in df.iterrows():
        ir_match = ir_regex.search(row['message'])
        red_match = red_regex.search(row['message'])
        green_match = green_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}

        if ir_match:
            parsed_data['IR'] = int(ir_match.group(1))
        if red_match:
            parsed_data['Red'] = int(red_match.group(1))
        if green_match:
            parsed_data['green'] = int(green_match.group(1))
        PPG.append(parsed_data)

    PPG_params = pd.DataFrame(PPG)
    PPGtable = PPG_params.dropna(subset=['IR', 'Red', 'green'], how='all', axis=0)
    PPGtable = PPGtable.reset_index(drop=True)
    PPGtable['datetime'] = pd.to_datetime(PPGtable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    PPGtable['time_round'] = PPGtable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    gyro = []
    for index, row in df.iterrows():
        Gx_match = Gx_regex.search(row['message'])
        Gy_match = Gy_regex.search(row['message'])
        Gz_match = Gz_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}
        if Gx_match:
            parsed_data['Gx'] = int(Gx_match.group(1))
        if Gy_match:
            parsed_data['Gy'] = int(Gy_match.group(1))
        if Gz_match:
            parsed_data['Gz'] = int(Gz_match.group(1))
        gyro.append(parsed_data)

    gyro_params = pd.DataFrame(gyro)
    gyrotable = gyro_params.dropna(subset=['Gx', 'Gy', 'Gz'], how='all', axis=0)
    gyrotable = gyrotable.reset_index(drop=True)
    gyrotable['datetime'] = pd.to_datetime(gyrotable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    gyrotable['time_round'] = gyrotable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    acc = []
    for index, row in df.iterrows():
        Ax_match = Ax_regex.search(row['message'])
        Ay_match = Ay_regex.search(row['message'])
        Az_match = Az_regex.search(row['message'])
        # Temp_match = Temp_regex.search(row['message'])
        # EMG_match = EMG_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}
        if Ax_match:
            parsed_data['Ax'] = int(Ax_match.group(1))
        if Ay_match:
            parsed_data['Ay'] = int(Ay_match.group(1))
        if Az_match:
            parsed_data['Az'] = int(Az_match.group(1))
        acc.append(parsed_data)

    acc_params = pd.DataFrame(acc)
    acctable = acc_params.dropna(subset=['Ax', 'Ay', 'Az'], how='all', axis=0)
    acctable = acctable.reset_index(drop=True)
    acctable['datetime'] = pd.to_datetime(acctable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    acctable['time_round'] = acctable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    # try:
    emg_tmp = []
    for index, row in df.iterrows():
        Temp_match = Temp_regex.search(row['message'])
        EMG_match = EMG_regex.search(row['message'])
        parsed_data = {'datetime': row['datetime']}
        if Temp_match:
            parsed_data['Temp'] = int(Temp_match.group(1))
        if EMG_match:
            parsed_data['EMG'] = int(EMG_match.group(1))
        emg_tmp.append(parsed_data)

    emg_tmptable = pd.DataFrame(emg_tmp)
    emg_tmptable = emg_tmptable.dropna(subset=['Temp'], how='all', axis=0)
    emg_tmptable = emg_tmptable.reset_index(drop=True)
    emg_tmptable['datetime'] = pd.to_datetime(emg_tmptable['datetime'])
    # Round 'timestamp' column to nearest millisecond
    emg_tmptable['time_round'] = emg_tmptable['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])

    imu = pd.merge(gyrotable, acctable, on="time_round", how="inner")
    print("imu", imu)
    ppg = pd.merge(PPGtable, imu, on="time_round", how="inner")
    print("ppg", ppg)

    table = pd.merge(emg_tmptable, ppg, on="time_round", how="inner", suffixes=('time_round', 'time_round'))
    print("table", table)

    table = table.sort_index(axis=0, ascending=True).reset_index(inplace=False, drop=True)
    table = table.dropna()
    table = table.reset_index(drop=True)
    dat = table

    dat = dat[~(dat.isnull().any(axis=1))]  # remove nan
    dat = dat[~(dat.isin([np.inf, -np.inf]).any(axis=1))]  # remove inf
    dat = dat.reset_index(drop=True)
    print(dat.columns)
    ###############################################################################################
    # dat.fillna(method="ffill", inplace=True)
    print(emg_tmptable)

    return dat

# Example

# dirs = "C:/Users/logger/Patients/2023_08_28output.txt"
# # # dirs = "C:/Users/logger/Patients/2023_07_31output.txt"
# # # # file_name = "Forearm_Right_Rest_Sitting_0_data.csv"
# from_logger_to_csv1(dirs)

