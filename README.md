# awstools
Collection of AWS scripts
# Details
bucketexists.py: Checks if bucket exists or you are good to create it.
approver.py: Auto Approves a ACM Certificate Request. There was a manual step required when stacks come up and request a certificate. The stack for lambda function drops the emails in the s3 bucket.
S3 bucket generates an event and triggers the lambda.
lambda checks if its wildcard and rejects it, else approves it using mechanize library.
An email is sent in either case.
