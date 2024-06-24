import os
import numpy as np
import pandas as pd
import json
"""
This script convert json output (exported from dynamoDB to S3, and downloaded from s3 to local) into csv.
1. To export the DB table to S3 go to- https://us-east-1.console.aws.amazon.com/dynamodbv2/home?region=us-east-1#exports
2. In the source table use Alpha-SessionDataStreamingServiceStack-SessionDynamoTableCB26CEAA-Y5A2TJH1GPPD
3. Export to ggdynamo bucket s3://ggdynamo/AWSDynamoDB/
4. Download the file to your local comp. and change the directory_path and csv_path to your local paths. 
"""

# Example
directory_path = 'C:/Users/dalit/Documents/gainguard/data/log_ppg/logger/'
csv_path =  'C:/Users/dalit/Documents/gainguard/data/log_ppg/cal_exp/'
files = os.listdir(directory_path)
files = [file for file in files if os.path.isfile(os.path.join(directory_path, file))]

if files:
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(directory_path, x)))
    print("The most recent file is:", latest_file)

    # Extracting model name from the latest file name
    model_name = latest_file.split('.')[0]  # Assuming the model name is before the first period in the file name

else:
    print("No files found in the directory.")
file_path = f"{directory_path + str(latest_file)}"
print(file_path)
import pandas as pd
import numpy as np
import json


def read_last_lines(file_path, num_lines):
    dfs = []
    with open(file_path, 'r') as file:
        lines = file.readlines()[-num_lines:]
        for line in lines:
            data = json.loads(line)
            ir_values = data['NewImage']['irValues']['L']
            gyro_values = data['NewImage']['gyroValues']['L']
            accel_values = data['NewImage']['accelValues']['L']

            if len(ir_values) >= 3 and len(gyro_values) >= 3 and len(accel_values) >= 3:
                df = pd.DataFrame([{
                    'userId': data['Keys']['userId']['S'],
                    'datetime': pd.to_datetime(int(data['Keys']['timestamp']['N']), unit='ms', utc=True),
                    'time_round': pd.to_datetime(int(data['Keys']['timestamp']['N']), unit='ms', utc=True)
                                  .strftime('%H:%M:%S.%f')[:-5],
                    'connectionId': data['NewImage']['connectionId']['S'],
                    'areaName': data['NewImage']['areaName']['S'],
                    'Temp': float(data['NewImage']['temperature']['N']),
                    'EMG': float(data['NewImage']['emg']['N']),
                    'IR': float(ir_values[0]['N']),
                    'Red': float(ir_values[1]['N']),
                    'green': float(ir_values[2]['N']),
                    'Gx': float(gyro_values[0]['N']),
                    'Gy': float(gyro_values[1]['N']),
                    'Gz': float(gyro_values[2]['N']),
                    'Ax': float(accel_values[0]['N']),
                    'Ay': float(accel_values[1]['N']),
                    'Az': float(accel_values[2]['N']),
                }])
                dfs.append(df)
    datas = pd.concat(dfs)
    return datas


dir=read_last_lines(file_path,20000)
dir.to_csv(csv_path + str(latest_file) + ".csv")
print(dir)




