def lambda_handler(event, context):
    import boto3
    
    query_1 =   "SELECT from_iso8601_timestamp(eventTime) AS \"Timestamp\", \
                requestparameters, \
                sourceipaddress \
                FROM cloudtrail_xxxxx_cloudtrail_logs_anshu_li \
                WHERE (( requestparameters LIKE '{\"x-amz-acl\":\"public%') \
                        OR (requestparameters LIKE '%http://acs.amazonaws.com/groups/global/AllUsers%')) \
                        AND (eventsource <> 'athena.amazonaws.com') \
                        AND (from_iso8601_timestamp(eventTime) > now() - interval '1' hour) \
                ORDER BY  eventtime desc;"
                

    database = "default"
    s3_output = "s3://s3-athena-xxxxxx-anshu/"
    
    client = boto3.client('athena')
    
    response = client.start_query_execution(QueryString = query_1,
                                        QueryExecutionContext={
                                            'Database': database
                                        },
                                        ResultConfiguration={
                                            'OutputLocation': s3_output
                                        }
                                        )
    print response
