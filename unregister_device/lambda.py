import sys
import logging
import conf
import psycopg2
import boto3
import json
import time

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# load config
try:
    Config = conf.load_config('$LATEST')
except Exception as e:
    logger.error("ERROR: couldn't load conf file")
    sys.exit()


try:
    db_conn = psycopg2.connect(database=Config['DATABASE']['db'], user=Config['DATABASE']['user'],
                               password=Config['DATABASE']['password'],
                               host=Config['DATABASE']['host'], port=Config['DATABASE']['port'])
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to datbase instance.")
    sys.exit()

try:
    sns_client = boto3.client('sns')
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to sns instance.")
    sys.exit()

logger.info("SUCCESS: Connection to DATABASE and SNS instance succeeded")


def handler(event, context):
    """
    @api {DELETE} https://4r3r9b19u9.execute-api.us-east-1.amazonaws.com/prod unregister_device
    @apiName unregister_device
    @apiGroup Device
    @apiDescription unregister  device
    @apiVersion 0.1.0
    @apiHeader {String} x-api-key api-key.
    @apiParam {String} device_token       Mandatory
    @apiParamExample {json} Example:
    {
        "payload":
        {
            "device_token": "a6181119 3c02a69f c689f523 1a86da85 39e7b77c d0504d2a 20fd0c48 8ab8fae8"
        }
    }
    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
              code='200', message='success',
              data={
              },
              metadata={}
        }
    """
    try:
        logger.info(event)
        payload = event.get('payload')
        endpoint_arn = __get_arn(payload['device_token'])
        __unregister_endpoint(endpoint_arn)
        __delete_endpoint(endpoint_arn)
        return get_raw_response_message(code=200, message='success', data={})
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __get_arn(device_token):
    user_endpoint = None
    select_query = """
          SELECT arn FROM {table_name}
          WHERE token = '{device_token}'
          """.format(**{
        'table_name': Config['DATABASE']['tables']['users_endpoints'],
        'device_token': device_token,
    })

    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                user_endpoint = dict(zip(keys, list(row)))
                print(user_endpoint['arn'])
            return user_endpoint['arn']
    except Exception as e:
        with db_conn.cursor() as cur:
            cur.execute("ROLLBACK;")
        raise Exception("device token doesn't exists")

def __unregister_endpoint(endpoint_arn):
    try:
        sns_client.delete_endpoint(EndpointArn=endpoint_arn)
        return True
    except Exception as e:
        raise e


def __delete_endpoint(endpoint_arn):
    delete_query = """
        DELETE FROM {table_name}
        WHERE arn = '{endpoint_arn}';
    """.format(**{
        'table_name': Config['DATABASE']['tables']['users_endpoints'],
        'endpoint_arn': endpoint_arn,
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(delete_query)
            db_conn.commit()
            logger.info(cur.statusmessage)
    except Exception as e:
        raise e

def get_raw_response_message(code=200, message='', data={}, metadata={}, status_code=200):
    response = dict(code=code, message=message, data=data, metadata=metadata, timestamp=time.time())
    return response