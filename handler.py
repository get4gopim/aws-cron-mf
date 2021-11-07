import json

from domain import FundInfo
from datetime import datetime
from service import HtmlParser2
from service import MFService


def hello(event, context):
    print ('update all started :: ' + datetime.now().__str__())

    funds_list = MFService.get_all_funds()

    for fund_info in funds_list:
        print(fund_info)
        fund_url = fund_info.get_mfUrl()
        info = HtmlParser2.call_fund_api(fund_url)
        mf = FundInfo.FundInfo(fund_info.get_mfId(), fund_info.get_mfUrl(), info.get_mfName(), info.get_asOn(), info.get_nav(), datetime.now().__str__())
        MFService.update_fund(mf)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    print('update all completed :: ' + datetime.now().__str__())

    return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    event = {}
    context = {}
    hello(event, context)