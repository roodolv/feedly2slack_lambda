import logging.config
import traceback
import os
import json
import base64
import boto3
import requests

def decryptionUrl(encrypted_environ):
    decrypted_environ = boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(encrypted_environ))['Plaintext']
    return 'https:{}'.format(
       decrypted_environ.decode('utf-8')
    )

# get environ
error_slack_url = decryptionUrl(os.environ.get('ERROR_SLACK_URL', None))
error_slack_channel = os.environ.get('ERROR_SLACK_CHANNEL', None)
log_level = os.environ.get('LOG_LEVEL', 'ERROR')

# debug settings
def logger_level(level):
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
logger.setLevel(logger_level(log_level))

def lambda_handler(event, context):
    try:
        # get enviton
        slack_url = decryptionUrl(os.environ.get('SLACK_URL', None))
        slack_channel = os.environ.get('SLACK_CHANNEL', None)

        # data to slack
        if not('Records' in event):
            return event

        records = event['Records']
        for record in records:

            if not('dynamodb' in record):
                continue

            if not('NewImage' in record['dynamodb']):
                continue

            feed = record['dynamodb']['NewImage']
            art_title = feed['art_title']['S']
            art_url = feed['art_url']['S']
            author_name = feed['author_name']['S']
            author_url = feed['author_url']['S']

            # If a feed doesn't have any image, the Feedly official logo will be set.
            # This script may catch an error if fails to get an image file.
            if 'art_image_url' in feed:
                art_image_url = feed['art_image_url']['S']
            else:
                art_image_url = 'https://s5.feedly.com/images/feedly-512.png'

            if 'written_by' in feed:
                written_by = ' by ' + feed['written_by']['S']
            else:
                written_by = ' '

            if 'summary' in feed:
                summary = feed['summary']['S'][0:100] + '....'
            # Settng half-width space for script not to stop.
            else:
                summary = ' '

            # this is the right way to write with 'blocks' in Slack API
            requests.post(
                slack_url,
                json.dumps(
                    {
                        'blocks': [
                            	   {
                                       'type': 'section',
                                       'text': {
                                           'type': 'mrkdwn',
                                           'text': '*<{art_url}|{art_title}>*\n<{author_url}|{author_name}>{written_by}\n{summary}'.format(
                                               art_url = art_url,
                                               art_title = art_title,
                                               author_url = author_url,
                                               author_name = author_name,
                                               written_by = written_by,
                                               summary = summary
                                           )
                                       },
                                       'accessory': {
                                           'type': 'image',
                                           'image_url': art_image_url,
                                           'alt_text': ' '
                                       }
                                   }
                        ]
                    }
                )
            )

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
                                        'text': 'dynamo_to_slack error\n{message}'.format(
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