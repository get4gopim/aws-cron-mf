import boto3

from domain import FundInfo, MFHistory
from service import MFHistoryService, HtmlParser2
from botocore.exceptions import ClientError
from datetime import datetime


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
            fund_info.set_category(resp['category'])
            print('getAll_funds: ' + fund_info.get_mfName())
            fundList.append(fund_info)

    return fundList


def find_all_funds(dynamodb=None):
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
            fund_info = FundInfo.FundInfo(resp['mf_id'], resp['mf_url'], resp['mf_name'], resp['as_on'], resp['nav'], resp['last_updated'])
            fund_info.set_category(resp['category'])
            print('getAll_funds: ' + fund_info.get_mfName())
            fundList.append(fund_info)

    return fundList


def get_fund(mfId, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('mf_nav_latest')

    try:
        response = table.get_item(Key={'mf_id': mfId})
        print (response)
        resp = response['Item']
    except ClientError as e:
        print('Item not found' + e.response['Error']['Message'])
    else:
        if resp:
            print(resp)
            fund_info = FundInfo.FundInfo(resp['mf_id'], resp['mf_url'], resp['mf_name'], resp['as_on'],
                                          resp['nav'], resp['last_updated'])
            fund_info.set_category(resp['category'])
            print('get_fund: ' + fund_info.get_mfName())

        return fund_info


def add_fund(fundInfo, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('mf_nav_latest')

    print(str(fundInfo))
    fundInfo = fetch_fund_outbound(fundInfo)

    item = {
        'mf_id': fundInfo.get_mfId(),
        'as_on': fundInfo.get_asOn(),
        'mf_url': fundInfo.get_mfUrl(),
        'mf_name': fundInfo.get_mfName(),
        'category': fundInfo.get_category(),
        'last_updated': fundInfo.get_lastUpdated(),
        'nav': fundInfo.get_nav()
    }

    response = table.put_item(
       Item= item
    )

    MFHistoryService.add_mf_nav_history(mf_history=MFHistory.MFHistory(fundInfo.get_mfId(), fundInfo.get_asOn(),
                                                                       fundInfo.get_nav(), datetime.now().__str__()))

    return response


def fetch_fund_outbound(fund_info):
    fund_url = fund_info.get_mfUrl()
    info = HtmlParser2.call_fund_api(fund_url)
    mf = FundInfo.FundInfo(fund_info.get_mfId(), fund_info.get_mfUrl(), info.get_mfName(), info.get_asOn(),
                           info.get_nav(), datetime.now().__str__())
    mf.set_category(fund_info.get_category())
    return mf


def update_fund(fundInfo, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('mf_nav_latest')

    fundInfo = fetch_fund_outbound(fundInfo)

    response = table.update_item(
        Key={
            'mf_id': fundInfo.get_mfId()
        },
        UpdateExpression="set mf_name=:mfName, nav=:nav, as_on=:asOn, category=:category, last_updated=:lastUpdated",
        ExpressionAttributeValues={
            ':mfName': fundInfo.get_mfName(),
            ':nav': fundInfo.get_nav(),
            ':asOn': fundInfo.get_asOn(),
            ':category': fundInfo.get_category(),
            ':lastUpdated': fundInfo.get_lastUpdated()
        },
        ReturnValues="UPDATED_NEW"
    )

    MFHistoryService.add_mf_nav_history(mf_history=MFHistory.MFHistory(fundInfo.get_mfId(), fundInfo.get_asOn(),
                                                                       fundInfo.get_nav(), datetime.now().__str__()))

    return response
