import json
import urllib
import boto3

print('Loading function')

s3 = boto3.client('s3')


def load_config(env_alias):
    bucket = 'sns-lambda-config'
    key = 'config.json'
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        config = json.loads(response['Body'].read())
        return config[env_alias]
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e