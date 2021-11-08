import boto3

from service import MFService
from datetime import datetime
from domain import FundInfo, UserFund
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import And, Attr, Key
from decimal import Decimal


def update_user_mf_funds(user_id, mf_id, dynamodb=None):
    print ('user id: ' + user_id)
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('user_mf')

    response = table.scan( FilterExpression=Attr("user_id").eq(user_id) ) # FilterExpression=Attr("user_id").eq(user_id) & Attr("mf_id").eq(mf_id)
    print (str(response))
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    fundList = []
    for resp in data:
        if resp:
            print(resp)
            user_fund_info = UserFund.UserFund(resp['user_id'], resp['mf_id'], resp['purchase_value'], resp['purchase_nav'],
                                          resp['stamp_percent'], '', '', '', '', resp['date_created'], '')
            print('getAll_funds:: userId: ' + user_fund_info.get_userId() + " mfId: " + user_fund_info.get_mfId())
            fundList.append( update_mf(user_fund_info) )

    return fundList


def update_mf(user_fund_info):
    user_mf = None

    if user_fund_info:
        fund_info = MFService.get_fund( user_fund_info.get_mfId() )

        purchase_val = float(user_fund_info.get_purchaseValue())
        stamp_value = purchase_val * (float(user_fund_info.get_stampPercent()) / 100)

        actual_val = purchase_val - stamp_value
        units = round( actual_val / float(user_fund_info.get_purchaseNav()), 4)
        latest_val = round( float(units) * float(fund_info.get_nav()), 4)
        profit_loss = round( latest_val - purchase_val, 4)

        user_mf = UserFund.UserFund(user_fund_info.get_userId(), user_fund_info.get_mfId(), user_fund_info.get_purchaseValue(), user_fund_info.get_purchaseNav(),
                          user_fund_info.get_stampPercent(), actual_val, units, latest_val,
                          profit_loss, user_fund_info.get_dateCreated(), datetime.now().__str__())

        set_additional_fields(user_fund_info, fund_info)

        update_fund (user_mf)

    return user_mf


def get_all_user_funds(user_id, dynamodb=None):
    print('user id: ' + user_id)

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('user_mf')

    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    fundList = []
    for resp in data:
        if resp:
            print(resp)
            fund_info = MFService.get_fund(resp['mf_id'])
            user_fund_info = UserFund.UserFund(resp['user_id'], resp['mf_id'], resp['purchase_value'], resp['purchase_nav'],
                                          resp['stamp_percent'], resp['actual_value'], resp['units'], resp['latest_value'], resp['profit_loss'],
                                          resp['date_created'], resp['date_modified'])

            set_additional_fields(user_fund_info, fund_info)

            print('getAll_funds:: userId: ' + user_fund_info.get_userId() + " mfId: " + user_fund_info.get_mfId())
            fundList.append(user_fund_info)

    return fundList


def set_additional_fields(user_fund_info, fund_info):
    percentile = round((float(user_fund_info.get_profitLoss()) / float(user_fund_info.get_purchaseValue())) * 100, 2)

    user_fund_info.set_nav(fund_info.get_nav())
    user_fund_info.set_mfName(fund_info.get_mfName())
    user_fund_info.set_asOn(fund_info.get_asOn())
    user_fund_info.set_percentile(percentile)


def get_user_and_fund_by_id(user_id, mf_id, dynamodb=None):
    print ('user id: ' + user_id + ';  mf id: ' + mf_id)
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('user_mf')

    response = table.scan(FilterExpression=Attr("user_id").eq(user_id) & Attr("mf_id").eq(mf_id))
    print (str(response))
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    fundList = []
    for resp in data:
        if resp:
            print(resp)
            fund_info = MFService.get_fund(resp['mf_id'])
            user_fund_info = UserFund.UserFund(resp['user_id'], resp['mf_id'], resp['purchase_value'],
                                               resp['purchase_nav'],
                                               resp['stamp_percent'], resp['actual_value'], resp['units'],
                                               resp['latest_value'], resp['profit_loss'],
                                               resp['date_created'], resp['date_modified'])

            set_additional_fields(user_fund_info, fund_info)

    return fundList


def get_user_and_fund_by_id_123(user_id, mf_id, dynamodb=None):
    print ('user id: ' + user_id + ';  mf id: ' + mf_id)

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('user_mf')

    try:
        response = table.get_item(Key={'user_id': user_id, 'mf_id': mf_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print (str(response))
        resp = response['Item']
        if resp:
            print(resp)
            fund_info = MFService.get_fund(resp['mf_id'])
            user_fund_info = UserFund.UserFund(resp['user_id'], resp['mf_id'], resp['purchase_value'],
                                               resp['purchase_nav'],
                                               resp['stamp_percent'], resp['actual_value'], resp['units'],
                                               resp['latest_value'], resp['profit_loss'],
                                               resp['date_created'], resp['date_modified'])

            set_additional_fields(user_fund_info, fund_info)

        return user_fund_info


def add_user_id_and_fund(user_fund_info, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('user_mf')

    print(str(user_fund_info))

    item = {
        'user_id': user_fund_info.get_userId(),
        'mf_id': user_fund_info.get_mfId(),
        'purchase_value': user_fund_info.get_purchaseValue(),
        'purchase_nav': user_fund_info.get_purchaseNav(),
        'stamp_percent': user_fund_info.get_stampPercent(),
        'actual_value': user_fund_info.get_actualValue(),
        'units': user_fund_info.get_units(),
        'latest_value': user_fund_info.get_latestValue(),
        'profit_loss': user_fund_info.get_profitLoss(),
        'date_created': user_fund_info.get_dateCreated(),
        'date_modified': datetime.now().__str__()
    }

    response = table.put_item(
       Item= item
    )

    return response


def update_fund(fundInfo, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('user_mf')

    response = table.update_item(
        Key={
            'mf_id': fundInfo.get_mfId(),
            'user_id': fundInfo.get_userId()
        },
        UpdateExpression="set actual_value=:actual_value, units=:units, latest_value=:latest_value, profit_loss=:profit_loss, date_modified=:date_modified",
        ExpressionAttributeValues={
            ':actual_value': str(fundInfo.get_actualValue()),
            ':units': str(fundInfo.get_units()),
            ':latest_value': str(fundInfo.get_latestValue()),
            ':profit_loss': str(fundInfo.get_profitLoss()),
            ':date_modified': fundInfo.get_dateModified()
        },
        ReturnValues="UPDATED_NEW"
    )
    return response
