import json
import boto3
import os
import time
import logging
import requests
from adapter import convert_session_data_list_to_dataframe
import errors
from pred_to_DB import save_prediction_response

dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)



def handler(event, context):
    logger.info('event: {}'.format(json.dumps(event)))
    # get table name from env:
    table_name = os.environ['SESSION_DATA_TABLE_NAME']
    ml_container_dns = 'http://' + \
        os.environ['ML_MODEL_CONTAINER_DNS_NAME'] + '/predict/'
    payload = json.loads(event['body'])
    # payload = event
    if not payload:
        return JsonResponse({ "error": "not payload" }, status=400)
        
    if 'user_id' not in payload or 'area_name' not in payload or 'muscle_name' not in payload:
        return errors.BAD_REQUEST
    user_id = payload['user_id']
    area_name = payload['area_name']
    muscle_name = payload['muscle_name']
    end_timestamp = int(time.time() * 1000)
    start_timestamp = end_timestamp - 360000
    # start_timestamp = 0  # for testing
    if 'start_timestamp' in payload:
        start_timestamp = payload['start_timestamp']
    if 'end_timestamp' in payload:
        end_timestamp = payload['end_timestamp']

    logger.info('user_id: {}'.format(user_id))
    logger.info('area_name: {}'.format(area_name))
    logger.info('muscle_name: {}'.format(muscle_name))
    logger.info('start_timestamp: {}'.format(start_timestamp))
    logger.info('end_timestamp: {}'.format(end_timestamp))
    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="userId = :user_id AND #timestamp BETWEEN :start_timestamp AND :end_timestamp",
            FilterExpression="areaName = :area_name AND muscleName = :muscle_name",
            ExpressionAttributeValues={
                ':user_id': {'S': user_id},
                ':area_name': {'S': area_name},
                ':muscle_name': {'S': muscle_name},
                ':start_timestamp': {'N': str(start_timestamp)},
                ':end_timestamp': {'N': str(end_timestamp)}
            },
            ExpressionAttributeNames={
                '#timestamp': 'timestamp'
            },
            ScanIndexForward=False
        )
        if len(response['Items']) == 0:
            logger.info('no session data found')
            return errors.BAD_REQUEST
        logger.info("response[item][0]: {}".format(response['Items'][0]))
        df = convert_session_data_list_to_dataframe(response['Items']) #Working good until here
        prediction_response = requests.post(
            ml_container_dns, json=df.to_json(), data=df.to_json())
        logger.info('prediction response status code: {}'.format(
            prediction_response.status_code))


        if prediction_response.status_code != 200:
            logger.error('[model failed] prediction response: {}'.format(
                prediction_response.json()))
            return errors.PREDICTION_FAILED
        data = prediction_response.json()
        logger.info('prediction response: {}'.format(data))

        save_prediction_response(data['prediction'], user_id, area_name, muscle_name, end_timestamp)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(data)
        }
    except Exception as e:
        logger.error('exception: {}'.format(e))
        logger.exception(e)
        return errors.INTERNAL_SERVER_ERROR
