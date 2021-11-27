import flask
import logging
import os
import json

from flask import jsonify, request
from service import MFService, UserMFService, HtmlParser2, MFHistoryService
from domain import FundInfo, UserFund, MFHistory
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
    graph_data = MFHistoryService.graph_mf_history('user1', 'MES016')
    for key, value in graph_data.items():
        print(key, ' : ', value)
    return render_template('graph.html', graph_data=graph_data)


@app.route('/funds/<user_id>/update')
def funds_update(user_id=None):
    view_fund = UserMFService.view_update_user_mf_funds(user_id)
    return render_template('funds.html', view_fund=view_fund)


@app.route('/funds/<user_id>')
def funds(user_id=None):
    view_fund = UserMFService.view_all_user_mf_funds(user_id)
    return render_template('funds.html', view_fund=view_fund)


@app.route('/funds/<user_id>/history/<mf_id>/date/<purchase_date>')
def history_multiple(user_id=None, mf_id=None, purchase_date=None):
    print ('mf_id :: ' + mf_id + ' purchase_date :: ' + purchase_date)

    if purchase_date is not None:
        mf_id = mf_id + "#" + purchase_date
        print('altered mf_id :: ' + mf_id)

    view_history = MFHistoryService.view_mf_history(user_id, mf_id, purchase_date)
    return render_template('history.html', view_history=view_history)


@app.route('/funds/<user_id>/history/<mf_id>/sip')
def funds_sip(user_id=None, mf_id=None):
    print('mf_id :: ' + mf_id + ' user_id :: ' + user_id)
    view_fund = UserMFService.view_sip_user_mf_funds(user_id, mf_id)
    return render_template('funds_sip.html', view_fund=view_fund)
# ------------------------------------------ Funds User API -------------------


# A route to get fund by given id
@app.route('/api/v1/user/<user_id>/funds/update', methods=['GET'])
def api_get_user_fund(user_id):
    LOGGER.info("user_id: " + user_id )
    f_list = UserMFService.update_user_mf_funds(user_id)
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
    dateCreated = request.json.get('dateCreated')

    if not userId or not mfId or not dateCreated:
        return jsonify({'error': 'Please provide userId, mfId and dateCreated'}), 400

    user_fund_info = UserFund.UserFund(userId, mfId, request.json.get('purchaseValue'), request.json.get('purchaseNav'),
                                       request.json.get('stampPercent'), request.json.get('actualValue'),
                                       request.json.get('units'), request.json.get('latestValue'),
                                       request.json.get('profitLoss'), request.json.get('dateCreated'),
                                       datetime.now().__str__())
    user_fund_info.set_type(request.json.get('type'))

    response = UserMFService.add_user_id_and_fund(user_fund_info)

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
    category = request.json.get('category')

    if not id or not fund_url:
        return jsonify({'error': 'Please provide id and url'}), 400

    info = HtmlParser2.call_fund_api(fund_url)
    fundInfo = FundInfo.FundInfo(id, fund_url, info.get_mfName(), info.get_asOn(),
                                 info.get_nav(), datetime.now().__str__())
    fundInfo.set_category(category)

    response = MFService.add_fund(fundInfo)

    return jsonify(response)


# A route to update fund
@app.route('/api/v1/funds', methods=['PUT'])
def api_update_fund():
    LOGGER.info("api_add_fund: " + str(request))
    LOGGER.info("request.json: " + str(request.json))

    id = request.json.get('mfId')
    fund_url = request.json.get('mfUrl')
    category = request.json.get('category')

    if not id or not fund_url:
        return jsonify({'error': 'Please provide id and url'}), 400

    info = HtmlParser2.call_fund_api(fund_url)
    fundInfo = FundInfo.FundInfo(id, fund_url, info.get_mfName(), info.get_asOn(),
                                 info.get_nav(), datetime.now().__str__())
    fundInfo.set_category(category)
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

    mf.set_category(fund_info.get_category())

    response = MFService.update_fund(mf)
    print(response)

    body = {
        "statusCode": 200,
        "body": json.dumps(response)
    }

    return jsonify(response)


@app.route('/api/v1/history', methods=['POST'])
def api_funds_history():
    LOGGER.info("api_mf_history_add: " + str(request))
    LOGGER.info("request.json: " + str(request.json))

    id = request.json.get('mfId')
    asOn = request.json.get('asOn')

    if not id or not asOn:
        return jsonify({'error': 'Please provide id and asOn'}), 400

    response = MFHistoryService.add_mf_nav_history(mf_history=MFHistory.MFHistory(id, asOn,
                                                             request.json.get('nav'), datetime.now().__str__()))

    return jsonify(response)


@app.route('/api/v1/history/<id>', methods=['GET'])
def api_get_fund_history(id):
    print ('mf_id: ' + id)
    f_list = MFHistoryService.get_funds_history(id)
    serialized_list = [e.serialize() for e in f_list]
    return jsonify(serialized_list)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Mutual Fund API Running</h1>"

