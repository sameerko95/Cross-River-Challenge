import boto3
import time
import json

def lambda_handler(event, context):
    year = event["params"]["querystring"]["year"]
    s3 = boto3.client('s3')

    response = s3.select_object_content(
        Bucket='lending-club-crb',
        Key='loan.csv',
        ExpressionType='SQL',
        Expression="Select SUM(CAST(s.\"loan_amnt\" AS FLOAT)) loan_amnt, SUM(CAST(s.\"funded_amnt\" AS FLOAT))\
         funded_amnt, SUM(CAST(s.\"funded_amnt_inv\" AS FLOAT)) funded_amnt_inv from S3Object s WHERE s.\"issue_d\"\
            LIKE '%"+year+"%'",
        InputSerialization={
            'CSV': {
                    "FileHeaderInfo": "USE",
                    "RecordDelimiter": "\n",
                    "FieldDelimiter": ","
                    }
        },
        OutputSerialization={
            'JSON': {
                    "RecordDelimiter": "\n",
            }
        }
    )
    for event in response['Payload']:
        if 'Records' in event:
            records = json.loads(event['Records']['Payload'].decode('utf-8'))

    records["loan_amnt"] = int(round(records["loan_amnt"]))
    records["funded_amnt"] = int(round(records["funded_amnt"]))
    records["funded_amnt_inv"] = int(round(records["funded_amnt_inv"]))

    return records