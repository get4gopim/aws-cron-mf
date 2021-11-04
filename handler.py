import json

import boto3

from domain import FundInfo
from datetime import datetime
from decimal import Decimal
from service import HtmlParser2


def hello(event, context):
    print ('hello:: ' + datetime.now().__str__())

    mfAsOnDate = datetime.now().strftime("%d-%b-%Y")
    print ("date " + mfAsOnDate)

    info = HtmlParser2.call_hdfc_api()

    mf = FundInfo.FundInfo('MIB010', 'https://www.moneycontrol.com/mutual-funds/nav/idbi-ultra-short-term-fund/MIB009', info.get_mfName(), info.get_asOn(),  info.get_nav(), datetime.now().__str__())
    # add_fund(mf)
    update_fund(mf)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def add_fund(fundInfo, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('mf_nav_latest')

    print(str(fundInfo))

    item = {
        'mf_id': fundInfo.get_mfId(),
        'as_on': fundInfo.get_asOn(),
        'mf_url': fundInfo.get_mfUrl(),
        'mf_name': fundInfo.get_mfName(),
        'last_updated': fundInfo.get_asOn(),
        'nav': fundInfo.get_nav()
    }

    response = table.put_item(
       Item= item
    )

    return response


def update_fund(fundInfo, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('mf_nav_latest')

    response = table.update_item(
        Key={
            'mf_id': fundInfo.get_mfId()
        },
        UpdateExpression="set mf_name=:mfName, nav=:nav, as_on=:asOn, last_updated=:lastUpdated",
        ExpressionAttributeValues={
            ':mfName': fundInfo.get_mfName(),
            ':nav': Decimal(fundInfo.get_nav()),
            ':asOn': fundInfo.get_asOn(),
            ':lastUpdated': fundInfo.get_lastUpdated()
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    event = {}
    context = {}
    hello(event, context)