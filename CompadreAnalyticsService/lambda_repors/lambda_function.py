import boto3
import json
import logging
import os
from convert_response_to_dataframe import convert_response_to_dataframe
import errors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    logger.info('event: {}'.format(json.dumps(event)))
    
    # Get table name from environment variables
    table_name = os.environ.get('SESSION_DATA_TABLE_NAME')
    
    if not table_name:
        logger.error("SESSION_DATA_TABLE_NAME environment variable not set")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Internal server error: Table name not configured"})
        }
    
    logger.info('Using DynamoDB table: {}'.format(table_name))
    
    if 'body' in event:
        payload = json.loads(event['body'])
    else:
        payload = event

    if not payload:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "no payload"})
        }

    user_id = payload.get('user_id')
    muscle_name = payload.get('muscle_name')
    
    if not user_id or not muscle_name:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "missing user_id or muscle_name"})
        }

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression='#user_id = :user_id',
            FilterExpression='#muscle_name = :muscle_name',
            ExpressionAttributeValues={
                ':user_id': {'S': user_id},
                ':muscle_name': {'S': muscle_name}
            },
            ExpressionAttributeNames={
                '#user_id': 'userId',
                '#muscle_name': 'muscleName'
            }
        )

        if not response['Items']:
            logger.info('No session data found')
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "No session data found"})
            }

        logger.info("response[item][0]: {}".format(response['Items'][0]))

        # Convert the response to a list of dictionaries
        data_dicts = convert_response_to_dataframe(response)
        
        # Convert the list of dictionaries to JSON string
        response_body = json.dumps(data_dicts)
        
        # Load the JSON string to ensure proper formatting
        formatted_response_body = json.loads(response_body)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': formatted_response_body
        }

    except dynamodb.exceptions.ResourceNotFoundException as e:
        logger.error('DynamoDB table not found: {}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Internal server error: Table not found"})
        }
    except Exception as e:
        logger.error('Exception: {}'.format(e))
        logger.exception(e)
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Internal server error"})
        }
