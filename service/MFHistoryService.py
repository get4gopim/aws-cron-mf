import boto3

from datetime import datetime
from domain import MFHistory, ViewHistory
from service import MFService
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import And, Attr, Key


def add_mf_nav_history(mf_history, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('nav_history')

    print(str(mf_history))

    item = {
        'mf_id': mf_history.get_mfId(),
        'as_on': mf_history.get_asOn(),
        'nav': mf_history.get_nav(),
        'date_modified': datetime.now().__str__()
    }

    response = table.put_item(
       Item= item
    )

    return response


def get_funds_history(mf_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('nav_history')

    response = table.query(
        KeyConditionExpression=Key('mf_id').eq(mf_id),
        ScanIndexForward=False,
    )
    print (str(response))
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    mf_fund = MFService.get_fund(mf_id)

    historyList = []
    for resp in data:
        if resp:
            print(resp)
            mf_history = MFHistory.MFHistory(resp['mf_id'], resp['as_on'], resp['nav'], resp['date_modified'])
            mf_history.set_mfName(mf_fund.get_mfName())
            print(str(mf_history))
            historyList.append(mf_history)

    return historyList


def view_mf_history(mf_id):
    historyList = get_funds_history(mf_id, None)
    return transform_view_history(historyList)


def transform_view_history(historyList):
    view_history = ViewHistory.ViewHistory()
    view_history.set_historyList(historyList)
    return view_history