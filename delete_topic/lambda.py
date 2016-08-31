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
    @api {DELETE} /topic delete_topic
    @apiName delete_topic
    @apiGroup Topic
    @apiDescription delete topic
    @apiVersion 0.1.0
    @apiHeader {String} x-api-key api-key.
    @apiParam {String} topic_name       Mandatory
    @apiParamExample {json} Example:
    {
        "payload":
        {
            "topic_name": "topic_name"
        }
    }
    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
              code='200', message='success',
              data={
                      topic_arn {String}
              },
              metadata={}
        }
    """
    try:
        logger.info(event)
        payload = event.get('payload')
        topic_arn = __get_topic_arn(payload['topic_name'])
        __delete_topic(topic_arn)
        __delete_topic_from_db(topic_arn)
        return get_raw_response_message(code=200, message='success', data={'topic_arn': topic_arn})
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __delete_topic(topic_arn):
    try:
        sns_client.delete_topic(TopicArn=topic_arn)
        return True
    except Exception as e:
        raise e

def __get_topic_arn(topic_name):
    topic = None
    select_query = """
          SELECT arn FROM {table_name}
          where name = '{topic_name}'
          """.format(**{
        'table_name':  Config['DATABASE']['tables']['topics'],
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

def __delete_topic_from_db(topic_arn):
    delete_query = """
        DELETE FROM {table_name}
        WHERE arn = '{topic_arn}';
    """.format(**{
        'table_name': Config['DATABASE']['tables']['topics'],
        'topic_arn': topic_arn,
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
