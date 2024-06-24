import logging
import boto3
from datetime import datetime, timezone

# Initialize the DynamoDB client and logger
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def save_prediction_response(prediction_response, user_id, area_name, muscle_name, end_timestamp):
    try:
        keys_to_convert = ['risk_of_injury', 'warm_up', 'intensity', 'recovery', 'body_connection']
        
        # Convert values associated with keys to numeric types
        for key in keys_to_convert:
            if key in prediction_response:
                try:
                    prediction_response[key] = float(prediction_response[key])  # Convert value to float
                except ValueError:
                    logger.warning(f"Failed to convert '{key}' value to float.")

        logger.info(
            f"Saving item with Key: userId={user_id}, areaName={area_name}, muscleName={muscle_name}, end_timestamp={end_timestamp}")

        # Get the current datetime in UTC timezone
        current_datetime = datetime.now(timezone.utc)
        current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        
        response = dynamodb.put_item(
            TableName='predvalue',
            Item={
                'userId': {'S': user_id},  # Ensure userId attribute matches the partition key
                'areaName': {'S': area_name},
                'muscleName': {'S': muscle_name},
                'timestamp': {'N': str(end_timestamp)},
                'risk_of_injury': {'N': str(prediction_response.get('risk_of_injury', 0))},
                'warm_up': {'N': str(prediction_response.get('warm_up', 0))},
                'intensity': {'N': str(prediction_response.get('intensity', 0))},
                'recovery': {'N': str(prediction_response.get('recovery', 0))},
                'body_connection': {'N': str(prediction_response.get('body_connection', 0))},
                'datetime': {'S': current_datetime_str}  # Convert datetime to string
            }
        )

        logger.info('Prediction response saved to DynamoDB')  # Logging statement for successful operation
    except Exception as e:
        logger.error('Failed to save prediction response to DynamoDB: {}'.format(e))


