from django.shortcuts import render
# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
from model.transform import transform
from model.summarize import summarize
from model.constants import *
from model.save_report1 import save_csv_to_s3
import logging
# from model.convert_response_to_dataframe import convert_response_to_dataframe

logging.basicConfig(level=logging.INFO)  # required for info logs to show up
logger = logging.getLogger()
logger.setLevel(logging.INFO)

@csrf_exempt
#TODO: clean the nested try-atch blocks
def predict(request):
    if request.method == 'POST':
        # Deserialize the request body to a Pandas DataFrame
        try:
            body = json.loads(request.body)
            df = pd.DataFrame.from_dict(body)
            # if len(df) < 100:
            #     return JsonResponse({'prediction': {
            #         RISK_OF_INJURY: 0,
            #         WARMP_UP: 0,
            #         INTENSITY: 0,
            #         RECOVERY: 0,
            #         BODY_CONNECTION: 0
            #     }})
            try:
                # Call the XGBoost model to predict on the DataFrame
                transformed = transform(df)
                
                summary_result = summarize(transformed)
                user_id = transformed['userId'].unique()[0]
                muscle_name = transformed['muscleName'].unique()[0]
        
                try:
                    ######Save to S3##################################################################################
                    save_csv_to_s3(user_id,muscle_name,transformed,summary_result, filename='past_week')
                    ###################################################################################################
                except Exception as e:
                    logger.error("Error saving to S3: %s", e)
               
                return JsonResponse({'prediction': summarize(transformed)})
            except Exception as e:
                logger.exception(e)
                return JsonResponse({'error' , e}, status = 500)

        except Exception as e:
            logger.exception(e)
            return JsonResponse({'error', e},status = 500)
    else:
        return JsonResponse({'error': 'Invalid request method'})


def index(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'Welcome to GainGuard Athlete Analytics Service!',
                             'request': 'Please send a POST request to /predict/ with a JSON body containing a dataframe of session data.',
                             'return format': json.dumps({'prediction': {
                                 RISK_OF_INJURY: 0,
                                 WARMP_UP: 0,
                                 INTENSITY: 0,
                                 RECOVERY: 0,
                                 BODY_CONNECTION: 0

                             }})})
    elif request.method == 'POST':
        return predict(request)
    else:
        return JsonResponse({'error': 'Invalid request method'})



# def reports(request):
#     if request.method == 'POST':
#         try:
#             body = json.loads(request.body)
#             # df = pd.DataFrame.from_dict(body)
#             try:
#                 report = convert_response_to_dataframe(response)
#             except Exception as e:
#                     logger.error("Error saving to S3: %s", e)

#             return JsonResponse({'Report': report})
#             except Exception as e:
#                 logger.exception(e)
#                 return JsonResponse({'error', e}, status=500)

#         except Exception as e:
#             logger.exception(e)
#             return JsonResponse({'error', e}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid request method'})





