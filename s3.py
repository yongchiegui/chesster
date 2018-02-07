import boto3
import csv
import json
import io

with open('config.json', 'r') as f:
    config = json.load(f)

AWS_ACCESS_KEY_ID = config['AWS']['ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS']['SECRET_ACCESS_KEY']
RATINGS_FORMAT = config['GENERAL']['RATING_FORMAT']
S3_BUCKET_NAME = config['AWS']['S3']['BUCKET_NAME']
S3_FILE_NAME = config['AWS']['S3']['FILE_NAME']


def get_ratings_from_s3():
    """Gets ratings from s3 file"""
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3_object = s3.Object(S3_BUCKET_NAME, S3_FILE_NAME)
    ratings_string = s3_object.get()['Body'].read()
    rating_string_io = io.BytesIO(ratings_string)
    ratings_dict_reader = csv.DictReader(rating_string_io)

    ratings_dict = {}
    for player in ratings_dict_reader:
        ratings_dict[player['name']] = int(player['rating'])

    return ratings_dict


def store_ratings_to_s3(ratings_dict):
    """Save ratings file to s3"""
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3_object = s3.Object(S3_BUCKET_NAME, S3_FILE_NAME)

    ratings_string = RATINGS_FORMAT + '\r\n'
    for key, value in ratings_dict:
        ratings_string = ratings_string + key + ',' + str(value) + '\r\n'

    s3_object.put(Body=ratings_string)