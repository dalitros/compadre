import numpy as np
import pandas as pd
import os
import boto3
import io
from datetime import datetime,timedelta, timezone

s3 = boto3.client('s3')

def save_csv_to_s3(user_id, muscle_name, transformed, summary_result, filename='past_week'):
    prediction = []
    try:
        # Save to S3
        avg_datetime = datetime.now(timezone.utc)
        # avg_datetime = transformed['datetime'].mean()
        avg_datetime_str = avg_datetime.strftime('%Y-%m-%d %H:%M:%S')
        summary_result['Avg_DateTime'] = avg_datetime_str
        prediction.append(summary_result)
        df_with_predictions = pd.DataFrame(prediction)
    except Exception as e:
        print("Error creating DataFrame: ", e)
        return

    bucket_name = 'ggdynamo'
    folder_name = f'sumtable/{user_id}/{muscle_name}/'
    file_name = f'{filename}.csv'
    s3_key = f'{folder_name}{file_name}'

    try:
        s3.head_object(Bucket=bucket_name, Key=folder_name)
    except Exception as e:
        print("Folder does not exist or error checking: ", e)
        # Create folder if it doesn't exist
        try:
            s3.put_object(Bucket=bucket_name, Key=folder_name)
            print("Folder created: ", folder_name)
        except Exception as e:
            print("Error creating folder: ", e)
            return

    try:
        updated_csv_buffer = io.StringIO()
        df_with_predictions.to_csv(updated_csv_buffer, index=False)
        s3.put_object(Body=updated_csv_buffer.getvalue(), Bucket=bucket_name, Key=s3_key)
        print(f"Data saved to S3: {s3_key}")
    except Exception as e:
        print("Error saving to S3: ", e)
