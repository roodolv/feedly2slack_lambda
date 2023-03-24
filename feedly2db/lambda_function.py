import logging.config
import traceback
import os
import time
import json
import base64
import boto3
import requests
from datetime import datetime, timedelta

def decryptionUrl(encrypted_environ):
    decrypted_environ = boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(encrypted_environ))['Plaintext']
    return 'https:{}'.format(
       decrypted_environ.decode('utf-8')
    )

def decryption(encrypted_environ):
    decrypted_environ = boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(encrypted_environ))['Plaintext']
    return decrypted_environ.decode('utf-8')

# get environ
error_slack_url = decryptionUrl(os.environ.get('ERROR_SLACK_URL', None))
error_slack_channel = os.environ.get('ERROR_SLACK_CHANNEL', None)
log_level = os.environ.get('LOG_LEVEL', 'ERROR')

def loggerLevel(level):
    if level == 'CRITICAL':
        return 50
    elif level == 'ERROR':
        return 40
    elif level == 'WARNING':
        return 30
    elif level == 'INFO':
        return 20
    elif level == 'DEBUG':
        return 10
    else:
        return 0

logger = logging.getLogger()
logger.setLevel(loggerLevel(log_level))

def lambda_handler(event, context):
    try:
        # get environ
        feedly_url = decryptionUrl(os.environ.get('FEEDLY_URL', None))
        feedly_token = decryption(os.environ.get('FEEDLY_TOKEN', None))
        table_name = os.environ.get('DYNAMO_TABLE', None)
        interval_minute = os.environ.get('INTERVAL_MINUTE', None)
        feed_count = int(os.environ.get('FEED_COUNT', 100))

        # feedly get feed
        if interval_minute is None:
            interval_time = datetime.now() - timedelta(days=7)
        else:
            interval_time = datetime.now() - timedelta(minutes=int(interval_minute))

        unix_time = int(time.mktime(interval_time.timetuple())) * 1000
        logger.debug(unix_time)

        headers = {'Authorization': feedly_token}
        response_stream = requests.get(
            '{url}&count={count}&newerThan={time}'.format(
                url=feedly_url,
                count=feed_count,
                time=unix_time
            ),
            headers=headers
        )
        stream_data = json.loads(response_stream.text)
        logger.debug(stream_data)

        if not ('items' in stream_data):
            return

        stream_datas = stream_data['items']

        # to dynamo
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        for stream in stream_datas:
            logger.debug(stream)
            item = {
                'id': stream['id'],
                'art_title': stream['title'],
                'art_url': stream['alternate'][0]['href'],
                'author_name': stream['origin']['title'],
                'author_url': stream['origin']['htmlUrl']
            }
            if 'enclosure' in stream:
                item['art_image_url'] = stream['enclosure'][0]['href']

            if 'author' in stream:
                item['written_by'] = stream['author']

            if 'summary' in stream:
                item['summary'] = stream['summary']['content']

            response = table.put_item(
                Item=item
            )
            logger.debug(response)

    except:
        logger.error(traceback.format_exc())
        requests.post(
            error_slack_url,
            json.dumps(
                    {
                        'blocks': [
                                {
                                    'type': 'section',
                                    'text': {
                                        'type': 'plain_text',
                                        'text': 'feedly_to_dynamo error\n{message}'.format(
                                            message=traceback.format_exc()
                                        )
                                    }
                                }
                        ]
                    }
            )
        )

    finally:
        return event