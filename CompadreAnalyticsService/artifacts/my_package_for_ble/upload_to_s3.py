
from datetime import datetime
import boto3


def csv_to_s3 (dat):
    # current_time = datetime.now().strftime('_%H%M_%m%d%Y.csv')
    current_time = datetime.now().strftime('_%m%d%Y.csv')

    # Upload the CSV string to S3
    # Uploading the csv to s3
    s3 = boto3.resource('s3')
    bucket_name = 'ggoutput'
    object_key = 'cal_exp/'
    object_name = current_time + 'output.csv'
    file_name = dat.to_csv(index=False)

    # Upload the CSV string to S3
    s3.Object(bucket_name, object_name).put(Body=file_name.encode('utf-8'))
    print(f'DataFrame saved to S3 bucket {bucket_name} with object name {object_name}')

