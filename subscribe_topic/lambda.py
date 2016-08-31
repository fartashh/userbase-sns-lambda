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
    @api {POST} /subscribe subscribe_topic
    @apiName subscribe_topic
    @apiGroup Subscription
    @apiDescription subscribe to topic
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
        user_arn = __get_user_arn(payload['user_id'])
        topic_arn = __get_topic_arn(payload['topic_name'])
        subscription_arn = __subscribe_topic(topic_arn, 'application', user_arn)
        __save_subscription(payload['user_id'], payload['topic_name'], subscription_arn)
        return get_raw_response_message(code=200, message='success', data={'subscription_arn': subscription_arn})
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __get_topic_arn(topic_name):
    topic = None
    select_query = """
          SELECT arn FROM {table_name}
          where name = '{topic_name}'
          """.format(**{
        'table_name': Config['DATABASE']['tables']['topics'],
        'topic_name': topic_name,
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                topic = dict(zip(keys, list(row)))

            return topic['arn']
    except Exception as e:
        with db_conn.cursor() as cur:
            cur.execute("ROLLBACK;")
        raise Exception("Topic name doesn't exists")


def __get_user_arn(user_id):
    user = None
    select_query = """
          SELECT arn FROM {table_name}
          where user_id = '{user_id}'
          """.format(**{
        'table_name': Config['DATABASE']['tables']['users_endpoints'],
        'user_id': user_id,
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                user = dict(zip(keys, list(row)))

            return user['arn']
    except Exception as e:
        with db_conn.cursor() as cur:
            cur.execute("ROLLBACK;")
        raise ("User id doesn't exists")


def __subscribe_topic(topic_arn, protocol, end_point):
    try:
        response = sns_client.subscribe(TopicArn=topic_arn, Protocol=protocol, Endpoint=end_point)
        return response['SubscriptionArn']
    except Exception as e:
        raise e


def __save_subscription(user_id, topic_name, subscription_arn):
    insert_query = """
        INSERT INTO {table_name}(
                user_id, topic_name, arn)
        VALUES ('{user_id}', '{topic_name}', '{subscription_arn}');
    """.format(**{
        'table_name': Config['DATABASE']['tables']['subscriptions'],
        'user_id': user_id,
        'topic_name': topic_name,
        'subscription_arn': subscription_arn
    })
    with db_conn.cursor() as cur:
        try:
            cur.execute(insert_query)
            db_conn.commit()
            logger.info(cur.statusmessage)
        except Exception as e:
            with db_conn.cursor() as cur:
                cur.execute("ROLLBACK;")
            raise e


def get_raw_response_message(code=200, message='', data={}, metadata={}, status_code=200):
    response = dict(code=code, message=message, data=data, metadata=metadata, timestamp=time.time())
    return response
