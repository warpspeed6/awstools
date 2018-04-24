def lambda_handler(event, context):
    import boto3
    
    
    query_1 =   "select * from alb_logs_table;"
                 
    database = "alb_logs"
    s3_output = "s3://XXXX-athena-results/"
    
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

