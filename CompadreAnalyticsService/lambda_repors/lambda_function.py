import boto3
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
# import requests
import errors
from convert_response_to_dataframe import convert_response_to_dataframe

logging.basicConfig(level=logging.INFO)  # required for info logs to show up
logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3 = boto3.client('s3')

dynamodb = boto3.client('dynamodb', region_name='us-east-1')



def lambda_handler(event, context):
    logger.info('event: {}'.format(json.dumps(event)))
    # get table name from env:
    table_name = os.environ['SESSION_DATA_TABLE_NAME']
    payload = json.loads(event['body'])

    if not payload:
        return JsonResponse({"error": "not payload"}, status=400)
    user_id = payload['user_id']
    # area_name = payload['area_name']
    muscle_name = payload['muscle_name']
    
    end_timestamp = int(time.time() * 1000)
    start_timestamp = end_timestamp - 604800000 # Week in ms

    try:
        response = dynamodb.query(
            TableName='predvalue',
            KeyConditionExpression='#user_id = :user_id AND #ts BETWEEN :start_time AND :end_time',
            FilterExpression="#muscle_name = :muscle_name",
            ExpressionAttributeValues={
                ':user_id': {'S': user_id},
                ':muscle_name': {'S': muscle_name},
                ':start_time': {'N': str(start_timestamp)},
                ':end_time': {'N': str(end_timestamp)}
            },
            ExpressionAttributeNames={
                '#user_id': 'userId',
                '#ts': 'timestamp',
                '#muscle_name': 'muscleName'
            },
            ScanIndexForward=False
        )

        if len(response['Items']) == 0:
            logger.info('no session data found')
            return errors.BAD_REQUEST
        logger.info("response[item][0]: {}".format(response['Items'][0]))

        # df = convert_response_to_dataframe(response)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response)}

    except Exception as e:
        logger.error('exception: {}'.format(e))
        logger.exception(e)
        return errors.INTERNAL_SERVER_ERROR

