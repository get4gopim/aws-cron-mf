import boto3

from service import MFService
from datetime import datetime
from domain import FundInfo, UserFund, ViewFund
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr, Key, And
from functools import reduce


def view_update_user_mf_funds(user_id):
    fundList = update_user_mf_funds(user_id, None)
    return transform_view_fund(fundList)


def view_all_user_mf_funds(user_id):
    fundList = reduce_user_mf_funds(user_id)
    return transform_view_fund(fundList)


def view_sip_user_mf_funds(user_id, mf_id):
    fundList = get_user_and_fund_by_id(user_id, mf_id)
    return transform_view_fund(fundList)


def reduce_user_mf_funds(user_id):
    fundList = get_all_user_funds(user_id, None)

    user_dict = {}
    fund_list = []

    for user_fund in fundList:
        mf_id_list = user_fund.get_mfId().split("#")
        mf_id = mf_id_list[0]

        if mf_id in user_dict: # Update Element
            old_fund = user_dict[mf_id]

            percentile = round(float(old_fund.get_percentile()) + float(user_fund.get_percentile()), 2)
            user_fund.set_percentile(percentile)

            pur_val = int(old_fund.get_purchaseValue()) + int(user_fund.get_purchaseValue())
            user_fund.set_purchaseValue(pur_val)

            profit_loss = round( (float(old_fund.get_profitLoss()) + float(user_fund.get_profitLoss()) ), 4)
            user_fund.set_profitLoss(profit_loss)

            user_dict[mf_id] = user_fund
        else: # Add Element
            user_dict[mf_id] = user_fund

    for key, value in user_dict.items():
        fund_list.append(value)

    return fund_list


def transform_view_fund(fundList):
    view_fund = ViewFund.ViewFund()
    view_fund.set_fundList(fundList)

    if fundList:
        total_purchase_val = 0
        total_profit = 0
        eq_total_purchase_val = 0
        eq_total_profit = 0
        total_percentile = 0
        eq_total_percentile = 0

        try:
            for item in fundList:
                if item.get_fundInfo().get_category() == "debt":
                    total_purchase_val += float(item.get_purchaseValue())
                    total_profit += float(item.get_profitLoss())
                elif item.get_fundInfo().get_category() == "equity":
                    eq_total_purchase_val += float(item.get_purchaseValue())
                    eq_total_profit += float(item.get_profitLoss())
        except BaseException as ex:
            print (f'Unable to calculate percentile : {item.get_fundInfo().get_mfName()} exception:: {repr(ex)}')

        if total_purchase_val != 0:
            total_percentile = round( (total_profit / total_purchase_val) * 100, 4 )

        if eq_total_purchase_val != 0:
            eq_total_percentile = round((eq_total_profit / eq_total_purchase_val) * 100, 4)

        view_fund.set_totalInvestment(total_purchase_val)
        view_fund.set_totalProfit(round(total_profit, 4))
        view_fund.set_totalPercentile(total_percentile)

        view_fund.set_eqInvestment(eq_total_purchase_val)
        view_fund.set_eqProfit(eq_total_profit)
        view_fund.set_eqPercentile(eq_total_percentile)

    return view_fund


def update_user_mf_funds(user_id, dynamodb=None):
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
            user_fund_info.set_type(resp['invest_type'])

            print('getAll_funds:: userId: ' + user_fund_info.get_userId() + " mfId: " + user_fund_info.get_mfId())
            fundList.append( update_mf(user_fund_info) )

    return fundList


def update_mf(user_fund_det):
    user_fund_info = None

    if user_fund_det:
        mf_id_list = user_fund_det.get_mfId().split("#")
        mf_id = mf_id_list[0]

        fund_info = MFService.get_fund( mf_id )

        purchase_val = float(user_fund_det.get_purchaseValue())
        stamp_value = purchase_val * (float(user_fund_det.get_stampPercent()) / 100)

        actual_val = purchase_val - stamp_value
        units = round( actual_val / float(user_fund_det.get_purchaseNav()), 4)
        latest_val = round( float(units) * float(fund_info.get_nav()), 4)
        profit_loss = round( latest_val - purchase_val, 4)

        user_fund_info = UserFund.UserFund(user_fund_det.get_userId(), user_fund_det.get_mfId(), user_fund_det.get_purchaseValue(), user_fund_det.get_purchaseNav(),
                          user_fund_det.get_stampPercent(), actual_val, units, latest_val,
                          profit_loss, user_fund_det.get_dateCreated(), datetime.now().__str__())
        user_fund_info.set_type(user_fund_det.get_type())

        set_additional_fields(user_fund_info, fund_info)

        update_fund (user_fund_info)

    return user_fund_info


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
            mf_id_list = resp['mf_id'].split("#")
            mf_id = mf_id_list[0]

            if len(mf_id_list) > 1:
                mf_purchase_date = mf_id_list[1]

            fund_info = MFService.get_fund(mf_id)
            user_fund_info = UserFund.UserFund(resp['user_id'], resp['mf_id'], resp['purchase_value'], resp['purchase_nav'],
                                          resp['stamp_percent'], resp['actual_value'], resp['units'], resp['latest_value'], resp['profit_loss'],
                                          resp['date_created'], resp['date_modified'])
            user_fund_info.set_type(resp['invest_type'])

            set_additional_fields(user_fund_info, fund_info)

            print('getAll_funds:: userId: ' + user_fund_info.get_userId() + " mfId: " + user_fund_info.get_mfId())
            fundList.append(user_fund_info)

    return fundList


def set_additional_fields(user_fund_info, fund_info):
    if fund_info:
        percentile = 0

        try:
            percentile = round((float(user_fund_info.get_profitLoss()) / float(user_fund_info.get_purchaseValue())) * 100, 2)
        except BaseException as ex:
            print (f'Unable to calculate percentile : {fund_info.get_mfName()} :: {user_fund_info.get_profitLoss()} exception:: {repr(ex)}')

        user_fund_info.set_fundInfo(fund_info)
        #user_fund_info.set_nav(fund_info.get_nav())
        #user_fund_info.set_mfName(fund_info.get_mfName())
        #user_fund_info.set_asOn(fund_info.get_asOn())
        user_fund_info.set_percentile(percentile)
        user_fund_info.set_noOfDays( find_between_days(fund_info.get_asOn(), user_fund_info.get_dateCreated()) )
    else:
        print ('fund_info empty')


def find_between_days(today, previous):
    date_format = "%d-%b-%Y"
    b = datetime.strptime(today, date_format)
    a = datetime.strptime(previous, date_format)
    delta = b - a
    return delta.days


def get_user_and_fund_by_id(user_id, mf_id, dynamodb=None):

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    TABLE_NAME = 'user_mf'
    table = dynamodb.Table(TABLE_NAME)

    print('user_id: ' + user_id + ';  mf id: ' + mf_id)

    exp_attributes = {
          ':pkVal': user_id,
          ':skVal': mf_id
    }

    print (str(exp_attributes))

    response = table.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='user_id = :pkVal AND begins_with ( mf_id, :skVal )',
        ExpressionAttributeValues=exp_attributes,
        ScanIndexForward=False,
    )
    print (str(response))
    data = response['Items']

    return construct_user_mf_list(data, dynamodb, response)


def get_user_funds_by_date(user_id, mf_id, purchase_date, dynamodb=None):

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    TABLE_NAME = 'user_mf'
    table = dynamodb.Table(TABLE_NAME)

    print('user_id: ' + user_id + ';  mf id: ' + mf_id + ' ; purchase_date: ' + purchase_date)

    response = table.scan(
                    Select= 'ALL_ATTRIBUTES',
                    FilterExpression=Key('user_id').eq(user_id) & Key('mf_id').begins_with(mf_id) & Key('date_created').gte(purchase_date)
              )

    print (str(response))
    data = response['Items']

    return construct_user_mf_list(data, dynamodb, response)


def construct_user_mf_list(data, dynamodb, response):
    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    user_fund_list = []

    for resp in data:
        if resp:
            print(resp)

            mf_id_list = resp['mf_id'].split("#")
            mf_id = mf_id_list[0]

            fund_info = MFService.get_fund(mf_id)
            user_fund_info = UserFund.UserFund(resp['user_id'], resp['mf_id'], resp['purchase_value'],
                                               resp['purchase_nav'],
                                               resp['stamp_percent'], resp['actual_value'], resp['units'],
                                               resp['latest_value'], resp['profit_loss'],
                                               resp['date_created'], resp['date_modified'])
            user_fund_info.set_type(resp['invest_type'])
            set_additional_fields(user_fund_info, fund_info)
            user_fund_list.append(user_fund_info)

    return user_fund_list


def add_user_id_and_fund(user_fund_info, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

    table = dynamodb.Table('user_mf')

    print(str(user_fund_info))

    mf_id = user_fund_info.get_mfId() + "#" + user_fund_info.get_dateCreated()

    item = {
        'user_id': user_fund_info.get_userId(),
        'mf_id': mf_id,
        'purchase_value': user_fund_info.get_purchaseValue(),
        'purchase_nav': user_fund_info.get_purchaseNav(),
        'stamp_percent': user_fund_info.get_stampPercent(),
        'actual_value': user_fund_info.get_actualValue(),
        'units': user_fund_info.get_units(),
        'latest_value': user_fund_info.get_latestValue(),
        'profit_loss': user_fund_info.get_profitLoss(),
        'invest_type': user_fund_info.get_type(),
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
        UpdateExpression="set actual_value=:actual_value, units=:units, latest_value=:latest_value, profit_loss=:profit_loss, invest_type=:invest_type, date_modified=:date_modified",
        ExpressionAttributeValues={
            ':actual_value': str(fundInfo.get_actualValue()),
            ':units': str(fundInfo.get_units()),
            ':latest_value': str(fundInfo.get_latestValue()),
            ':profit_loss': str(fundInfo.get_profitLoss()),
            ':invest_type': fundInfo.get_type(),
            ':date_modified': fundInfo.get_dateModified()
        },
        ReturnValues="UPDATED_NEW"
    )
    return response
