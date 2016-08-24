import sys
import logging
import conf
import psycopg2
import boto3
import json
import time
from datetime import datetime

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
    try:
        now = datetime.now()
        now = now.replace(second=0, microsecond=0)
        __send_notifications(now)
        __delete_notifications(now)
        logger.info('success')
        return True
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __delete_notifications(now):
    delete_query = """
              DELETE FROM {table_name}
              where date_trunc('minute',fire_at) < '{now}'
              """.format(**{
        'table_name': Config['DATABASE']['tables']['notifications'],
        'now': now
    })

    try:
        with db_conn.cursor() as cur:
            cur.execute(delete_query)
            db_conn.commit()
            logger.info(cur.statusmessage)
    except Exception as e:
        raise e


def __send_notifications(now):
    n_notification, n_failed = 0, 0
    select_query = """
              SELECT arn, message, is_topic FROM {table_name}
              where date_trunc('minute',fire_at) < '{now}'
              """.format(**{
        'table_name': Config['DATABASE']['tables']['notifications'],
        'now': now
    })

    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                notification = dict(zip(keys, list(row)))
                try:
                    [publish_message_to_device, publish_message_to_topic][notification['is_topic']](notification['arn'],
                                                                                                notification['message'])
                    n_notification+=1
                except Exception as e:
                    n_failed+=1
                    logger.exception(e)
            logger.info("n_notification:{}, n_failed:{}".format(n_notification, n_failed))
    except Exception as e:
        raise e

def publish_message_to_device(arn, message):
    try:
        sns_client.publish(Message=message, TargetArn=arn, MessageStructure='json')
    except Exception as e:
        raise e


def publish_message_to_topic(arn, message):
    try:
        sns_client.publish(Message=message, TopicArn=arn, MessageStructure='json')
    except Exception as e:
        raise e


def get_raw_response_message(code=200, message='', data={}, metadata={}, status_code=200):
    response = dict(code=code, message=message, data=data, metadata=metadata, timestamp=time.time())
    return response
