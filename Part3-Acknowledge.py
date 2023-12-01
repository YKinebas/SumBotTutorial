'''
Returns immediate response to Slack to fulfil API 3s response requirements
Verifies that the Slack request is authentic
If valid, Passes the the entire event to an SQS que that feeds into SumBot,
which is the function that interacts with the LLM API
'''
import json
import boto3
from datetime import datetime
import sys
import logging
import os
from slack_sdk import signature

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('sqs')
SIGNING_SECRET = os.environ['SIGNING_SECRET']
QUEUE_URL = os.environ['QUEUE_URL']

def lambda_handler(event, context):

    #verify that the request is from Slack
    try:
        body = str(event['body'])
        timestamp = str(event['headers']['X-Slack-Request-Timestamp'])
        sig = str(event['headers']['X-Slack-Signature'])

        if signature.SignatureVerifier(SIGNING_SECRET).is_valid(
            body = body,
            timestamp = timestamp,
            signature = sig
            ) == False:
            print("Failed to authenticate request") #to be replaced with a logger
            return {
                'statusCode': 401
            }
        else:
            print(str(signature.SignatureVerifier(SIGNING_SECRET).is_valid(body = body,
            timestamp = timestamp,
            signature = sig
            )))
            print("Successfully validated request") #to be replaced with a logger
            pass
    except Exception as e:
        logger.error("EXCEPTION: Error Verifying Slack request")
        logger.error(e)
        return {
            'statusCode': 401
            }
    
    #send sqs message with the current date & time
    response = client.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=str(event)
        )
    return {
        'statusCode': 200,
        'body': json.dumps(str(event))
    }