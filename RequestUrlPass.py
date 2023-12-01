'''
Code to pass Slack's URL verification
'''

import json

def lambda_handler(event, context):
    
    #Print event for debugging
    print("Event received:" + str(event))
    
    #Passing initial link validation
    body = json.loads(event["body"])
    print("Body: " + str(body))
    challenge = body["challenge"]
    print(challenge)
    return {
    'statusCode': 200,
    'body' : challenge
    }