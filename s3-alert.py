import boto3
import json
import logging
import re
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from base64 import b64decode
import urllib

s3 = boto3.client('s3')

def lambda_handler(event, context):
        response_url = "https://hooks.slack.com/services/TAV1N98HJ/BAV1R299A/xxxxxxxxxxxxxxxxxxxx"

        email_content = ''
        num_lines = 0

        # retrieve bucket name and file_key from the S3 event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        logger.info('Reading {} from {}'.format(file_key, bucket_name))
        # get the object
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        # get lines inside the csv
        lines = obj['Body'].read().split(b'\n')
        for r in lines:
                email_content = email_content + '\n' + r.decode()
                num_lines += 1

        email_content = "```"+email_content+"```"
        if num_lines > 2:
                response = { "text" : "Hello <!channel|>!. \nWe Found some public files in S3 Buckets :skull_and_crossbones:"+email_content, "channel": "general", "username": "DevSecOps"}
                slack_response = requests.post(response_url,json=response, headers={'Content-Type': 'application/json'})
                return slack_response.status_code
