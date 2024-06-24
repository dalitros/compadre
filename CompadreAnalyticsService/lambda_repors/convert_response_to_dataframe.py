import boto3
# import pandas as pd

s3 = boto3.client('s3')


# from save_report import save_csv

def convert_response_to_dataframe(response):
    # Extract the 'Items' from the response
    items = response['Items']

    # Initialize an empty list to store dictionaries for each item
    data_dicts = []

    # Iterate over each item in the response
    for item in items:
        # Convert each item to a dictionary suitable for DataFrame
        data_dict = {key: val['N'] if 'N' in val else val['S'] for key, val in item.items()}
        # Append the dictionary to the list
        data_dicts.append(data_dict)


    return data_dicts