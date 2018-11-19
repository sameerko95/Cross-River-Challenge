import boto3
import time
import json

def lambda_handler(event, context):
    # Fetch year from get request parameters
    year = event["params"]["querystring"]["year"]
    s3 = boto3.client('s3')

    # Perform S3 Select query to fetch required chunk of data from csv file
    response = s3.select_object_content(
        Bucket='lending-club-crb',
        Key='loan.csv',
        ExpressionType='SQL',
        Expression="Select s.\"loan_amnt\", s.\"funded_amnt\", s.\"funded_amnt_inv\", s.\"grade\", s.\"sub_grade\", s.\"issue_d\" from S3Object s WHERE s.\"issue_d\"\
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

    # Build the data in string format
    records = ""
    for event in response['Payload']:
        if 'Records' in event:
            records += event['Records']['Payload'].decode('utf-8')

    records = records.split("\n")

    monthVolume = {}
    creditBasedLoans = {}

    # Calculate the required aggregates credit wise and month wise    
    for row in records[:-1]:
        row = json.loads(row)
        month = row["issue_d"].split("-")[0]

        if month in monthVolume:
            monthVolume[month] += 1
        else:
            monthVolume[month] = 1

        grade = row['grade']
        if grade in creditBasedLoans:
            if month in creditBasedLoans[grade]:
                creditBasedLoans[grade][month][0] += float(row["loan_amnt"])
                creditBasedLoans[grade][month][1] += 1
            else:
                creditBasedLoans[grade][month] = [float(row["loan_amnt"]), 1]
        else:
            temp ={}
            temp[month] = [float(row["loan_amnt"]), 1]
            creditBasedLoans[grade] = temp

    # Calculate the average loan amount for a given grade and month
    for grade in creditBasedLoans:
        for month in creditBasedLoans[grade]:
            creditBasedLoans[grade][month] = creditBasedLoans[grade][month][0]/creditBasedLoans[grade][month][1]

    graphData = {"monthlyVolume": monthVolume, "creditBasedAvg": creditBasedLoans}
    return graphData