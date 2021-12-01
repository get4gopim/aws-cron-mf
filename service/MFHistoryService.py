from operator import attrgetter

import boto3

from datetime import datetime
from domain import MFHistory, ViewHistory
from service import MFService, UserMFService
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
        'nav': str(mf_history.get_nav()),
        'date_modified': datetime.now().__str__()
    }

    response = table.put_item(
       Item= item
    )

    return response


def get_funds_history(mf_id, user_fund=None, purchase_date=None, dynamodb=None, sortAsc=False):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('nav_history')

    response = table.query(
        KeyConditionExpression=Key('mf_id').eq(mf_id), # & Key('as_on').gte(purchase_date),
        ScanIndexForward=sortAsc,
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
            #print(resp)
            mf_history = MFHistory.MFHistory(resp['mf_id'], resp['as_on'], resp['nav'], resp['date_modified'])
            mf_history.set_mfName(mf_fund.get_mfName())

            if user_fund:
                as_on_value = round(float(user_fund.get_units()) * float(mf_history.get_nav()), 2)
                mf_history.set_asOnValue(as_on_value)

            #print(str(mf_history))
            historyList.append(mf_history)

    return historyList


def graph_mf_history(user_id, mf_id):
    user_fund_list = UserMFService.get_user_and_fund_by_id(user_id, mf_id)
    user_fund = user_fund_list[0]

    mf_id_list = mf_id.split("#")
    mf_id = mf_id_list[0]

    historyList = get_funds_history(mf_id, user_fund, None, None, sortAsc=True)

    print(str(historyList))

    sorted_list = sorted(historyList, key=lambda mfhistory: mfhistory.navdate)
    #sorted_list = sorted(historyList, key=attrgetter('navdate'))

    print ('sorted_list :: ' + str(sorted_list))

    return transform_view_history(sorted_list, user_fund_list)

    #graph_data = {}
    #for history in historyList:
    #    graph_data[float(history.get_nav())] = str(history.get_asOn())

    #return historyList


def view_mf_history(user_id, mf_id, purchase_date):
    user_fund_list = UserMFService.get_user_and_fund_by_id(user_id, mf_id)
    user_fund = user_fund_list[0]

    mf_id_list = mf_id.split("#")
    mf_id = mf_id_list[0]
    # if len(mf_id_list) > 1:
    #    mf_purchase_date = mf_id_list[1]
    purchase_dt = datetime.strptime(purchase_date, "%d-%b-%Y")

    historyList = get_funds_history(mf_id, user_fund, purchase_date, None)

    return transform_view_history(historyList, user_fund_list, purchase_dt)


def transform_view_history(historyList, user_fund_list, purchase_dt):
    view_history = ViewHistory.ViewHistory()

    if user_fund_list:
        user_fund = user_fund_list[0]
        fund_info = user_fund.get_fundInfo()
        view_history.set_userFund(user_fund)

        nav_diff = round(float(fund_info.get_nav()) - float(user_fund.get_purchaseNav()), 4)
        view_history.set_navDiff(nav_diff)

    historyList = filter(lambda mfhistory: mfhistory.navdate >= purchase_dt, historyList)
    historyList = sorted(historyList, key=lambda mfhistory: mfhistory.navdate, reverse=True)
    sorted_list = reversed(historyList) #sorted(historyList, key=lambda mfhistory: mfhistory.navdate)

    if historyList:
        for x in range(len(historyList)):
            mfHistory = historyList[x]
            if x < len(historyList)-1:
                next_hist_row = historyList[x+1]
                mfHistory.diffPrevAsOnValue = round(mfHistory.get_asOnValue() - next_hist_row.get_asOnValue(), 1)
                mfHistory.navGrowth = round(((mfHistory.get_nav() - user_fund.get_purchaseNav()) / user_fund.get_purchaseNav()) * 100, 2)

    historyList = historyList[:10]
    view_history.set_historyList(historyList)
    view_history.sortedList = sorted_list

    return view_history
