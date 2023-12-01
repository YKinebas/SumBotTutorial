'''
Processes SQS message rather than direct API
'''
#Built in modules:
import json
import ast
import os
from typing import Dict, Optional, Union
import signal
import logging

#Custom Layers
from slack_sdk import WebClient
import openai
from gpt import gpt

#Sets up the error logging process
#Optional, "logger" statements can be replaced with print()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

'''
SET ENV VARIABLES
'''
OPENAI_API_KEY  = os.environ['OPENAI_API_KEY']
SIGNING_SECRET = os.environ['SIGNING_SECRET']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']

#The function called when Lambda is invoked:
def lambda_handler(event, context):
   
   #This is a new addition
   #process SQS message
    try:
        records = event['Records'][0]
    except Exception as e:
        logger.error("EXCEPTION: Failed to read SQS")
        logger.error(e)
        print("ERROR: SQS Message parse error (Python <> Json conversion).")
        return {
        'statusCode': 500,
        }
    
    #The way you pull out the event body now also changes slightly
    try:
        body = json.loads(ast.literal_eval(records["body"])["body"])
        print(f"Event received...")
    except Exception as e:
        logger.error("EXCEPTION: Failed to get message body")
        logger.error(e)
        print("ERROR: Incoming message read error (Python <> Json conversion).")
        return {
        'statusCode': 500,
        }    
   
    #open slack and openai apis
    try:
        # Event API & Web API
        client = WebClient(SLACK_BOT_TOKEN)
        openai.api_key = OPENAI_API_KEY
    
    except Exception as e:
        logger.error("ERROR: Slack <> OpenAI Client Error")
        logger.error(e)
        print("ERROR: Slack / OpenAI Client Error.")
        return {
        'statusCode': 500,
        }
    
    #get prompt components from message
    try:
        postingUser = str(body["event"]["user"])
        userText = str(body["event"]["text"])
        print(f"Getting prompt elements...")
    except Exception as e:
        logger.error("ERROR: SQS Message parse error (Python <> Json conversion)")
        logger.error(e)
        print("ERROR: SQS Message parse error (Python <> Json conversion).")
        return {
        'statusCode': 500,
        }
    
    # Compile prompt for ChatGPT
    prompt = userText.split('>')[1]

    # Check ChatGPT
    try:
        gptresponse = gpt.summary(
            personality="",
            prompt=prompt
            )
    except Exception as e:
        logger.error("EXCEPTION: Timeout exception")
        logger.error(e)
        response = client.chat_postEphemeral(channel=body["event"]["channel"], 
                                        thread_ts=body["event"]["event_ts"],
                                        text=f"TimeoutException.",
                                        user=postingUser
                                        )
        return {
        'statusCode': 500,
        }
    
    #checks if called in thread
    try:
        isthread = body["event"]["thread_ts"]
        response = client.chat_postEphemeral(channel=body["event"]["channel"], 
                                            thread_ts=body["event"]["event_ts"],
                                            text=f"Here you go: \n{gptresponse}",
                                            user=postingUser
                                            )
        
        return {
            'statusCode': 200,
        }
    except KeyError:
        response = client.chat_postEphemeral(channel=body["event"]["channel"], 
                                            text=f"Here you go: \n{gptresponse}",
                                            user=postingUser
                                            )
        return {
            'statusCode': 200,
        }

    except Exception as e:
        logger.error("ERROR putting together response.")
        logger.error(e)
        response = client.chat_postEphemeral(channel=body["event"]["channel"], 
                                        thread_ts=body["event"]["event_ts"],
                                        text=f"Error putting together response.",
                                        user=postingUser)
        return {
        'statusCode': 500,
        }

