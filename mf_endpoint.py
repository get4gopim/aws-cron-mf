import flask
import logging
import os
import json

from flask import jsonify, request
from service import MFService, UserMFService, HtmlParser2
from domain import FundInfo, UserFund
from datetime import datetime

from flask import render_template

app = flask.Flask(__name__)
app.config["DEBUG"] = True

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')

LOGGER = logging.getLogger(__name__)

# ------------------------------------------ Web Page Render -------------------


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/funds/<user_id>')
def funds(user_id=None):
    f_list = UserMFService.update_user_mf_funds(user_id, None)
    return render_template('funds.html', f_list=f_list)
# ------------------------------------------ Funds User API -------------------


# A route to get fund by given id
@app.route('/api/v1/user/<user_id>/funds/<mf_id>', methods=['PUT'])
def api_get_user_fund(user_id, mf_id):
    LOGGER.info("user_id: " + user_id + " mf_id: " + mf_id)
    f_list = UserMFService.update_user_mf_funds(user_id, mf_id)
    serialized_list = [e.serialize() for e in f_list]
    return jsonify(serialized_list)


@app.route('/api/v1/user/<user_id>/funds', methods=['GET'])
def api_get_funds_by_user_id(user_id):
    LOGGER.info("api_get_funds_by_user_id")
    f_list = UserMFService.get_all_user_funds(user_id)
    serialized_list = [e.serialize() for e in f_list]
    return jsonify(serialized_list)


@app.route('/api/v1/user/<user_id>/funds/<mf_id>', methods=['GET'])
def get_user_and_fund_by_id(user_id, mf_id):
    LOGGER.info("get_user_and_fund_by_id")
    f_list = UserMFService.get_user_and_fund_by_id(user_id, mf_id)
    serialized_list = [e.serialize() for e in f_list]
    return jsonify(serialized_list)


@app.route('/api/v1/user/<user_id>/funds', methods=['POST'])
def api_user_add_fund(user_id):
    print("user_id: " + user_id)
    print("api_add_fund: " + str(request) )
    print("request.json: " + str(request.json) )

    userId = request.json.get('userId')
    mfId = request.json.get('mfId')

    if not userId or not mfId:
        return jsonify({'error': 'Please provide userId and mfId'}), 400

    response = UserMFService.add_user_id_and_fund(user_fund_info=UserFund.UserFund(userId, mfId, request.json.get('purchaseValue'), request.json.get('purchaseNav'),
                            request.json.get('stampPercent'), request.json.get('actualValue'), request.json.get('units'), request.json.get('latestValue'),
                            request.json.get('profitLoss'), request.json.get('dateCreated'), datetime.now().__str__() ) )

    return jsonify(response)


# ------------------------------------------ Funds API -------------------

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
    LOGGER.info("api_add_fund: " + str(request))
    LOGGER.info("request.json: " + str(request.json))

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
    print('update all started :: ' + datetime.now().__str__())

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

    print('update all completed :: ' + datetime.now().__str__())

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

