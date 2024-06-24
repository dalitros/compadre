import numpy as np
import pandas as pd
import os
import boto3
import io

s3 = boto3.client('s3')

def save_csv_to_s3(use_id,muscle_name,transformed,summary_result, filename='past_week'):
    ##################################################################
    # Save to S3
    avg_datetime = transformed['datetime'].mean()
    avg_datetime_str = avg_datetime.strftime('%Y-%m-%d %H:%M:%S')
    summary_result['Avg_DateTime'] = avg_datetime_str
    prediction.append(summary_result)
    df_with_predictions = pd.DataFrame(prediction)
    ##################################################################
    bucket_name = 'ggdynamo'
    folder_name = f'sumtable/{use_id}/{muscle_name}/'
    file_name = f'{filename}.csv'
    s3_key = f'{folder_name}{file_name}'
    try:
        s3.head_object(Bucket=bucket_name, Key=folder_name)
    except:
        s3.put_object(Bucket=bucket_name, Key=folder_name)

    updated_csv_buffer = io.StringIO()
    new_feature_means.to_csv(df_with_predictions, index=False)
    s3.put_object(Body=updated_csv_buffer.getvalue(), Bucket=bucket_name, Key=s3_key)
    print(f"Data saved to S3: {s3_key}")
