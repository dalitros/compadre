import json

NOT_FOUND = {
    'statusCode': 404,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'error': 'Not Found'})
}

INTERNAL_SERVER_ERROR = {
    'statusCode': 500,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'error': 'Internal Server Error'})
}

PREDICTION_FAILED = {
    'statusCode': 500,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'error': 'Prediction Failed'})
}

BAD_REQUEST = {
    'statusCode': 400,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'error': 'Bad Request'})
}

INSUFFICIENT_DATA = {
    'statusCode': 400,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'error': 'Insufficient Data'})
}
