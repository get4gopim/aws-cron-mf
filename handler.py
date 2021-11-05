import json

import boto3

from domain import FundInfo
from datetime import datetime
from service import HtmlParser2

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


def hello(event, context):
    print ('hello:: ' + datetime.now().__str__())

    mfAsOnDate = datetime.now().strftime("%d-%b-%Y")
    print ("date " + mfAsOnDate)

    #mf = FundInfo.FundInfo('MIB009', 'https://www.moneycontrol.com/mutual-funds/nav/idbi-ultra-short-term-fund/MIB009', info.get_mfName(), info.get_asOn(),  info.get_nav(), datetime.now().__str__())
    #add_fund(mf)
    #update_fund(mf)
    #fund_info = get_fund('MIB009')
    #print (fund_info.get_mfName())

    funds_list = get_all_funds()

    for fund_info in funds_list:
        print(fund_info)
        fund_url = fund_info.get_mfUrl()
        info = HtmlParser2.call_fund_api(fund_url)
        mf = FundInfo.FundInfo(fund_info.get_mfId(), fund_info.get_mfUrl(), info.get_mfName(), info.get_asOn(), info.get_nav(), datetime.now().__str__())
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


def get_all_funds(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('mf_nav_latest')

    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    fundList = []
    for resp in data:
        if resp:
            print(resp)
            fund_info = FundInfo.FundInfo(resp['mf_id'], resp['mf_url'], '', '', '', '')
            print('getAll_funds: ' + fund_info.get_mfName())
            fundList.append(fund_info)

    return fundList


def get_fund(mfId, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('mf_nav_latest')

    try:
        response = table.get_item(Key={'mf_id': mfId})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        resp = response['Item']
        if resp:
            print(resp)
            fund_info = FundInfo.FundInfo(resp['mf_id'], resp['mf_url'], resp['mf_name'], resp['as_on'],
                                          resp['nav'], resp['last_updated'])
            print('get_fund: ' + fund_info.get_mfName())

        return fund_info


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
            ':nav': fundInfo.get_nav(),
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