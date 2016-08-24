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
    @api {GET} https://bk3om565e4.execute-api.us-east-1.amazonaws.com/prod/ get_topics
    @apiName get_topics
    @apiGroup Topic
    @apiDescription get topics
    @apiVersion 0.1.0
    @apiHeader {String} x-api-key api-key.
    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
              code='200', message='success',
              data=[
                    {
                      "name": "News",
                      "arn": "arn:aws:sns:us-east-1:481790367918:News"
                    },
                    {
                      "name": "Test",
                      "arn": "arn:aws:sns:us-east-1:481790367918:Test"
                    }
                  ],
              metadata={}
        }
    """
    try:
        logger.info(event)
        data = __get_topics()
        return get_raw_response_message(code=200, message='success', data=data)
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def __get_topics():
    topics = []
    select_query = """
          SELECT name, arn FROM {table_name}
          """.format(**{
        'table_name': Config['DATABASE']['tables']['topics'],
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                topic = dict(zip(keys, list(row)))
                topics.append(topic)

            return topics
    except Exception as e:
        with db_conn.cursor() as cur:
            cur.execute("ROLLBACK;")
        raise e


def get_raw_response_message(code=200, message='', data={}, metadata={}, status_code=200):
    response = dict(code=code, message=message, data=data, metadata=metadata, timestamp=time.time())
    return response
