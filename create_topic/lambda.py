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
    :param event:
    event contains following key
        - payload : which contains
            - topic_name
    :param context:
    :return:
    """
    try:
        logger.info(event)
        payload = event.get('payload')
        topic_arn = __create_topic(payload['topic_name'])
        __save_topic(payload['topic_name'], topic_arn)
        return get_raw_response_message(code=200, message='success', data={'topic_arn': topic_arn})
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __create_topic(topic_name):
    try:
        response = sns_client.create_topic(Name=topic_name)
        return response['TopicArn']
    except Exception as e:
        raise (e)


def __save_topic(topic_name, topic_arn):
    insert_query = """
        INSERT INTO {table_name}(
                name, arn)
        VALUES ('{name}','{arn}');
    """.format(**{
        'table_name': Config['DATABASE']['tables']['topics'],
        'name': topic_name,
        'arn': topic_arn
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(insert_query)
            db_conn.commit()
            logger.info(cur.statusmessage)
    except Exception as e:
        with db_conn.cursor() as cur:
            cur.execute("ROLLBACK;")
        raise e


def get_raw_response_message(code=200, message='', data={}, metadata={}, status_code=200):
    response = json.dumps(dict(code=code, message=message, data=data, metadata=metadata, timestamp=time.time()))
    return response
