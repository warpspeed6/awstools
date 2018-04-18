import boto3
import mechanize
import os
import sys
from pprint import pprint
reload(sys)
sys.setdefaultencoding('utf8')
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_email(SUBJECT, BODY_HTML):
    client = boto3.client('ses',region_name='us-east-1')
    CHARSET="UTF-8"

    response = client.send_email(
        Destination={
            'ToAddresses': [
                'team@company.com.au',
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source='source-team@company.com.au',
    )

def get_s3_file_from_event(event):
    s3_client = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    s3_client.download_file(bucket, key, '/tmp/email_file')
    return '/tmp/email_file'

def parse_link_from_email_file(the_file):
    msg = open(the_file, 'r').readlines()
    for m in msg:
        if "https://ap-southeast-2.certificates.amazon.com/approvals?code" in m:
            logger.info('Link from parse_link_from_email_file is: {}'.format(m))

            return m.strip()

def parse_cert_id_from_email(the_file):
    msg = open(the_file, 'r').readlines()

    for m in msg:
        if "Certificate identifier: " in m:
            return m.split('r:')[1].strip()

def parse_domain_from_email(the_file):
    msg = open(the_file, 'r').readlines()

    for dom in msg:
        if "Domain: " in dom:
            return dom.split('n:')[1].strip()

def validate_acm_request(link):
    br = mechanize.Browser()
    br.open(link)
    response = br.response().read()
    if "Amazon Web Services (AWS) has received a request to issue an SSL certificate for *" in response:
        return True

def approve_link(link):
    def select_form(form):
        return form.attrs.get('action', None) == '/approvals'
    br = mechanize.Browser()
    br.open(link)
    response = br.response()
    br.select_form(predicate=select_form)
    br.submit()

def lambda_handler(event, context):
    logger.info('got event{}'.format(event))

    email_file = get_s3_file_from_event(event)
    link = parse_link_from_email_file(email_file)
    cert_id = parse_cert_id_from_email(email_file)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    domain = parse_domain_from_email(email_file)

    if validate_acm_request(link):
        logger.info("Not approving link due to wildcard")
        SUBJECT = "Wildcard Cert Approval Denied."
        BODY_HTML = """<html>
                    <head></head>
                    <body>
                      <h1>Wildcard Cert Approval Denied for %s</h1>
                      <p>'Certificate ID is: %s. File in s3 bucket is: https://s3.amazonaws.com/%s/%s'</p>
                    </body>
                    </html>
                    """ %(domain, cert_id, bucket, key)

    else:
        approve_link(link)
        logger.info(" Approving!!!")
        SUBJECT = "Certificate Request Approved."
        BODY_HTML = """<html>
                    <head></head>
                    <body>
                      <h1>ACM Certificate request Auto-Approved for %s</h1>
                      <p>'Certificate ID is: %s. File in s3 bucket is: https://s3.amazonaws.com/%s/%s'</p>
                    </body>
                    </html>
                    """ %(domain, cert_id, bucket, key)
    send_email(SUBJECT, BODY_HTML)
