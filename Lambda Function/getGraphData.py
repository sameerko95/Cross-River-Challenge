import boto3
import time
import json

def lambda_handler(event, context):
    year = event["params"]["querystring"]["year"]
    start_time = time.time()

    # year = event["params"]["querystring"]["year"]
    s3 = boto3.client('s3')

    response = s3.select_object_content(
        Bucket='lending-club-crb',
        Key='loan.csv',
        ExpressionType='SQL',
        Expression="Select s.\"loan_amnt\", s.\"funded_amnt\", s.\"funded_amnt_inv\", s.\"grade\", s.\"sub_grade\",\
         s.\"issue_d\" from S3Object s WHERE s.\"issue_d\" LIKE '%"+year+"%'",
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
    records = ""
    
    for event in response['Payload']:
        if 'Records' in event:
            records += event['Records']['Payload'].decode('utf-8')

    records = records.split("\n")
    monthVolume = {}

    creditBasedLoans = {}
    
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
                creditBasedLoans[grade][month].append(float(row["loan_amnt"]))
            else:
                creditBasedLoans[grade][month] = [float(row["loan_amnt"])]
        else:
            temp ={}
            temp[month] = [float(row["loan_amnt"])]
            creditBasedLoans[grade] = temp

    for grade in creditBasedLoans:
        for month in creditBasedLoans[grade]:
            creditBasedLoans[grade][month] = sum(creditBasedLoans[grade][month])/len(creditBasedLoans[grade][month])
    
    print(creditBasedLoans)
    print(monthVolume)
    # print("--- %s seconds ---" % (time.time() - start_time))

    graphData = {"month-volume": monthVolume, "credit-based-avg": creditBasedLoans}
    return graphData

lambda_handler(1,2)