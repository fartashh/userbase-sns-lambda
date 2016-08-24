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
    @api {DELETE} https://v141i5fp0j.execute-api.us-east-1.amazonaws.com/prod/ unsubscribe_topic
    @apiName unsubscribe_topic
    @apiGroup Subscription
    @apiDescription unsubscribe topic
    @apiVersion 0.1.0
    @apiHeader {String} x-api-key api-key.
    @apiParam {String} topic_name       Mandatory
    @apiParam {String} user_id          Mandatory
    @apiParamExample {json} Example:
    {
        "payload":
        {
            "topic_name": "topic_name",
            "user_id": "1"
        }
    }
    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
              code='200', message='success',
              data={
                      subscription_arn {String}
              },
              metadata={}
        }
    """
    try:
        logger.info(event)
        payload = event.get('payload')
        # get subscription arn
        subscription_arn = __get_subscribe_arn(payload['user_id'], payload['topic_name'])
        __unsubscribe_topic(subscription_arn)
        __delete_subscription(subscription_arn)

        return get_raw_response_message(code=200, message='success', data={'subscription_arn': subscription_arn})
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __get_subscribe_arn(user_id, topic_name):
    subscription = None
    select_query = """
          SELECT arn FROM {table_name}
          where topic_name = '{topic_name}' AND
          user_id = '{user_id}'
          """.format(**{
        'table_name': Config['DATABASE']['tables']['subscriptions'],
        'user_id': user_id,
        'topic_name': topic_name,
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                subscription = dict(zip(keys, list(row)))

            return subscription['arn']
    except Exception as e:
        with db_conn.cursor() as cur:
            cur.execute("ROLLBACK;")
        raise Exception("subscription doesn't exists")


def __unsubscribe_topic(subscription_arn):
    try:
        sns_client.unsubscribe(SubscriptionArn=subscription_arn)
        return True
    except Exception as e:
        raise e


def __delete_subscription(subscription_arn):
    delete_query = """
        DELETE FROM {table_name}
        WHERE arn = '{subscription_arn}';
    """.format(**{
        'table_name': Config['DATABASE']['tables']['subscriptions'],
        'subscription_arn': subscription_arn,
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
