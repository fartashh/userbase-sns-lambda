import sys
import logging
import conf
import psycopg2
import boto3
import json
import time
from datetime import datetime
import pytz

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
    @api {POST} https://92yq44217c.execute-api.us-east-1.amazonaws.com/prod/ send_notification
    @apiName send_notification
    @apiGroup Notification
    @apiDescription send or schedule notification to user or topic
    @apiVersion 0.1.0
    @apiHeader {String} x-api-key api-key.
    @apiParam {String}       user_id            Optional
    @apiParam {[String]}     topics_names       Optional
    @apiParam {Object}       query              Optional (based on user_data)
    @apiParam {String}       message            Mandatory
    @apiParam {Boolean}      is_json            Optional (default : false)
    @apiParam {Boolean}      send_in_user_timezone            Optional (default : false)
    @apiParam {Datetime}     fire_at            Optional ('%Y-%m-%d %H:%M:%S') if not provide notification send instantly

    @apiParamExample {json} Example:
    {
        "payload":
        {
            "message":"Notification",
            "user_id": "1",
            "is_json": false,
            "query": {"gender": "Male"},
            "topics_names": ["News"],
            "fire_at": "2016-08-24 21:42:40"
        }
    }
    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
              code='200', message='success',
              data={
                  "n_topic": 0,
                  "n_failed": 0,
                  "n_devices": 1
              },
              metadata={}
        }
    """
    try:
        not_success_count = 0
        payload = event.get('payload')
        user_id = payload.get('user_id', None)
        message = payload['message']
        is_json = payload.get('is_json', False)
        send_in_user_timezone = payload.get('send_in_user_timezone', False)
        fire_at = payload.get('fire_at', None)
        if fire_at:
            fire_at = pytz.utc.localize(datetime.strptime(fire_at, '%Y-%m-%d %H:%M:%S'))
        query = payload.get('query', None)
        topics_names = payload.get('topics_names', None)

        devices_by_id, devices_by_query=[],[]
        if user_id:
            devices_by_id = get_user_arns_by_id(user_id)
        if query:
            devices_by_query = get_user_arns_by_query(query)
        devices_by_id.extend(devices_by_query)

        topics = []
        if topics_names:
            topics = get_topics_arn(topics_names)

        # publish message
        if not fire_at:
            for device in devices_by_id:
                try:
                    message = prepare_message(message, is_json)
                    print(message)
                    publish_message_to_device(device['arn'], message)
                except Exception as e:
                    logger.exception(e)
                    not_success_count += 1
            for topic in topics:
                try:
                    message = prepare_message(message, is_json)
                    publish_message_to_topic(topic['arn'], message)
                except Exception as e:
                    logger.exception(e)
                    not_success_count += 1
        else:
            for device in devices_by_id:
                message = prepare_message(message, is_json)
                if send_in_user_timezone:
                    fire_at = localize_timezone(fire_at, device['user_timezone'])
                schedule_notification(device['arn'], message, fire_at, False)

            for topic in topics:
                message = prepare_message(message, is_json)
                schedule_notification(topic['arn'], message, fire_at, True)

        return get_raw_response_message(code=200, message='success',
                                        data={'n_topic':len(topics),'n_devices': len(devices_by_id), 'n_failed': not_success_count})
    except Exception as e:
        logger.exception(e)
        return get_raw_response_message(code=406, message=e.message, data={})


def get_user_arns_by_id(user_id):
    devices = []
    select_query = """
          SELECT arn, user_timezone FROM {table_name}
          WHERE user_id = '{user_id}'
          """.format(**{
        'table_name': Config['DATABASE']['tables']['users_endpoints'],
        'user_id': user_id
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                record = dict(zip(keys, list(row)))
                devices.append(record)
            return devices
    except Exception as e:
        raise e


def get_user_arns_by_query(query):
    devices = []
    select_query = """
          SELECT arn, user_timezone FROM {table_name}
          WHERE user_data = '{user_data}'
          """.format(**{
        'table_name': Config['DATABASE']['tables']['users_endpoints'],
        'user_data': json.dumps(query)
    })
    try:
        with db_conn.cursor() as cur:
            cur.execute(select_query)
            keys = [desc[0] for desc in cur.description]
            for row in cur:
                record = dict(zip(keys, list(row)))
                devices.append(record)
            return devices
    except Exception as e:
        raise e


def get_topics_arn(topics_names):
    topics = []
    select_query = """
          SELECT arn FROM {table_name}
          WHERE name in ({topics})
          """.format(**{
        'table_name': Config['DATABASE']['tables']['topics'],
        'topics': ", ".join("'{}'".format(topic) for topic in topics_names)
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


def schedule_notification(arn, message, fire_at, is_topic):
    insert_query = """
        INSERT INTO {table_name}(
                arn, message, fire_at, is_topic)
        VALUES ('{arn}', '{message}', '{fire_at}', '{is_topic}');
    """.format(**{
        'table_name': Config['DATABASE']['tables']['notifications'],
        'arn': arn,
        'message': message,
        'fire_at': fire_at,
        'is_topic': is_topic,
    })
    with db_conn.cursor() as cur:
        cur.execute(insert_query)
        db_conn.commit()
        logger.info(cur.statusmessage)


def prepare_message(message, is_json):
    if is_json:
        message_dict = json.loads(message)
    else:
        message_dict = {
            "default": message,
            "APNS": json.dumps({"aps": {"alert": message}}, ensure_ascii=False),
            "APNS_SANDBOX": json.dumps({"aps": {"alert": message}}, ensure_ascii=False),
            "GCM": json.dumps({"data": {"message": message}}, ensure_ascii=False)
        }

    return json.dumps(message_dict, ensure_ascii=False)


def get_raw_response_message(code=200, message='', data={}, metadata={}, status_code=200):
    response = dict(code=code, message=message, data=data, metadata=metadata, timestamp=time.time())
    return response

def localize_timezone(fire_at, user_timezone):
    local_tz = pytz.timezone(user_timezone)
    local_dt = fire_at.replace(tzinfo = local_tz)
    return local_dt.astimezone (pytz.utc)
