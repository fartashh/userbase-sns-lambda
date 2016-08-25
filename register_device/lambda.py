import sys
import logging
import conf
import psycopg2
import boto3
import json
import time
import allTimezones

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
    @api {POST} https://4r3r9b19u9.execute-api.us-east-1.amazonaws.com/prod register_device
    @apiName register_device
    @apiGroup Device
    @apiDescription register new device
    @apiVersion 0.1.0
    @apiHeader {String} x-api-key api-key.
    @apiParam {String} user_id            Mandatory
    @apiParam {String} user_timezone      Optional if not UTC
    @apiParam {String} device_token       Mandatory
    @apiParam {String} app                Mandatory
    @apiParam {Object} user_data          Optional
    @apiParamExample {json} Example:
    {
        "payload":
        {
            "device_token": "a6181119 3c02a69f c689f523 1a86da85 39e7b77c d0504d2a 20fd0c48 8ab8fae8",
            "app": "appname-ios-dev",
            "user_id": "1",
            "user_data": {"gender": "Male"}
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
        __is_valid(payload['device_token'], payload['user_id'])
        end_point_arn = __create_app_endpoint(payload['app'], payload['device_token'], payload['user_id'])
        user_timezone = allTimezones.validate_timezone(payload['user_timezone'])
        __save_user_endpoint(payload['app'], payload['device_token'], end_point_arn, payload['user_id'],
                             payload['user_data'], user_timezone)
        logger.info('success')
        return get_raw_response_message(code=200, message='success', data={})
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __save_user_endpoint(app, device_token, end_point_arn, user_id, user_data, user_timezone):
    insert_query = """
        INSERT INTO {table_name}(
                user_id, app, arn, token, user_data, user_timezone)
        VALUES ('{user_id}', '{app}', '{end_point_arn}', '{device_token}', '{user_data}', '{user_timezone}');
    """.format(**{
        'table_name': Config['DATABASE']['tables']['users_endpoints'],
        'app': app,
        'device_token': device_token,
        'user_id': user_id,
        'end_point_arn': end_point_arn,
        'user_data': json.dumps(user_data),
        'user_timezone':user_timezone
    })
    with db_conn.cursor() as cur:
        cur.execute(insert_query)
        db_conn.commit()
        logger.info(cur.statusmessage)


def __is_valid(device_token, user_id):
    """
    validate device_token and user_id
    you can update the logic anyhow suits you best
    :param device_token:
    :param user_id:
    :return:
    """
    select_query = """
          SELECT id FROM {table_name}
          where token = '{token}'
          """.format(**{
        'table_name':  Config['DATABASE']['tables']['users_endpoints'],
        'token': device_token,
    })

    with db_conn.cursor() as cur:
        cur.execute(select_query)
        row_count = cur.rowcount

    if row_count:
        raise Exception("device already registered")


def __create_app_endpoint(app, device_token, user_id):
    try:
        response = sns_client.create_platform_endpoint(
            PlatformApplicationArn=Config['APPLICATIONS'][app],
            Token=device_token,
            CustomUserData="'user_id':{}".format(user_id),
        )
        end_point_arn = response.get('EndpointArn')
        return end_point_arn
    except Exception as e:
        raise e


def get_raw_response_message(code=200, message='', data={}, metadata={}, status_code=200):
    response = dict(code=code, message=message, data=data, metadata=metadata, timestamp=time.time())
    return response