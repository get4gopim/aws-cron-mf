import flask
import logging
import os
import json

from flask import jsonify, request
from service import MFService, HtmlParser2
from domain import FundInfo
from datetime import datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')

LOGGER = logging.getLogger(__name__)


# A route to get all funds in db
@app.route('/api/v1/funds', methods=['GET'])
def api_get_all_funds():
    LOGGER.info("api_get_all_funds")
    f_list = MFService.find_all_funds()
    serialized_list = [e.serialize() for e in f_list]
    return jsonify(serialized_list)


# A route to add new fund
@app.route('/api/v1/funds', methods=['POST'])
def api_add_fund():
    LOGGER.info("api_add_fund: " + str(request) )
    LOGGER.info("request.json: " + str(request.json) )

    id = request.json.get('mfId')
    fund_url = request.json.get('mfUrl')

    if not id or not fund_url:
        return jsonify({'error': 'Please provide id and url'}), 400

    info = HtmlParser2.call_fund_api(fund_url)
    response = MFService.add_fund(fundInfo=FundInfo.FundInfo(id, fund_url, info.get_mfName(), info.get_asOn(),
                               info.get_nav(), datetime.now().__str__()) )

    return jsonify(response)


# A route to update fund
@app.route('/api/v1/funds', methods=['PUT'])
def api_update_fund():
    LOGGER.info("api_add_fund: " + request)
    LOGGER.info("request.json: " + request.json)
    id = request.json.get('mfId')
    fund_url = request.json.get('mfUrl')
    if not id or not fund_url:
        return jsonify({'error': 'Please provide id and url'}), 400

    info = HtmlParser2.call_fund_api(fund_url)
    response = MFService.update_fund(fundInfo=FundInfo.FundInfo(id, fund_url, info.get_mfName(), info.get_asOn(),
                                                             info.get_nav(), datetime.now().__str__()))

    return jsonify(response)


# A route to get fund by given id
@app.route('/api/v1/funds/<id>', methods=['GET'])
def api_get_fund(id):
    response = MFService.get_fund(id)
    return jsonify(response.serialize())


# A route to update the price for all funds - costlier operation
@app.route('/api/v1/funds/update/nav', methods=['GET'])
def update_price_all():
    funds_list = MFService.get_all_funds()

    resp_list = []
    for fund_info in funds_list:
        print(fund_info)
        fund_url = fund_info.get_mfUrl()
        info = HtmlParser2.call_fund_api(fund_url)
        mf = FundInfo.FundInfo(fund_info.get_mfId(), fund_info.get_mfUrl(), info.get_mfName(), info.get_asOn(),
                               info.get_nav(), datetime.now().__str__())
        response = MFService.update_fund(mf)
        resp_list.append(response)

    return jsonify(resp_list)


# A route to update the price for the particular fund id
@app.route('/api/v1/funds/update/nav/<id>', methods=['GET'])
def update_price(id):
    fund_info = MFService.get_fund(id)
    fund_url = fund_info.get_mfUrl()

    info = HtmlParser2.call_fund_api(fund_url)
    mf = FundInfo.FundInfo(fund_info.get_mfId(), fund_info.get_mfUrl(), info.get_mfName(), info.get_asOn(),
                           info.get_nav(), datetime.now().__str__())

    response = MFService.update_fund(mf)
    print(response)

    body = {
        "statusCode": 200,
        "body": json.dumps(response)
    }

    return jsonify(response)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Mutual Fund API Running</h1>"

