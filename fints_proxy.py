import logging
from stdnum import iban
from datetime import date
from datetime import datetime, timedelta
from fints.client import FinTS3PinTanClient, SEPAAccount
from dkb_robo import DKBRobo
from flask import Flask, abort
from flask import request
from flask import jsonify
import string
import os

app = Flask(__name__)

api_bank_list = {
    'dkb': {'url': 'https://banking-dkb.s-fints-pt-dkb.de/fints30', 'bic': 'BYLADEM1001', 'blz': '12030000'},
    'comdirect': {'url': 'https://fints.comdirect.de/fints', 'bic': 'COBADEHDXXX', 'blz': '20041111'},
    'ing': {'url': 'https://fints.ing-diba.de/fints/', 'bic': 'INGDDEFFXXX', 'blz': '50010517'}}


@app.route("/api/balance")
def balance():
    user = request.headers.get('user')
    pin = request.headers.get('pin')
    iban_num = request.args.get('iban')
    bank = request.args.get('bank').lower()
    if iban.is_valid(iban_num) is not True:
        abort(403)
    if not user:
        abort(403)
    if not pin:
        abort(403)
    if not bank:
        abort(403)

    url = api_bank_list[bank]['url']
    blz = api_bank_list[bank]['blz']
    bic = api_bank_list[bank]['bic']
    f = FinTS3PinTanClient(
        blz,  # Your bank's BLZ
        user,
        pin,
        url
    )
    account_balance = f.get_balance(SEPAAccount(iban_num, bic, iban_num[12:], '', blz))
    result = {'balance': str(account_balance.amount.amount)}
    return jsonify(result)


@app.route("/api/transactions")
def api_transactions():
    days = request.args.get('days')
    user = request.headers.get('user')
    pin = request.headers.get('pin')
    iban_num = request.args.get('iban')
    bank = request.args.get('bank').lower()
    if iban.is_valid(iban_num) is not True:
        abort(403)
    if not user:
        abort(403)
    if not pin:
        abort(403)
    if not bank:
        abort(403)
    url = api_bank_list[bank]['url']
    blz = api_bank_list[bank]['blz']
    bic = api_bank_list[bank]['bic']
    f = FinTS3PinTanClient(
        blz,  # Your bank's BLZ
        user,
        pin,
        url
    )
    date_N_days_ago = datetime.now() - timedelta(days=int(days))
    statements = f.get_statement(SEPAAccount(iban_num, bic, iban_num[12:], '', blz), date_N_days_ago, date.today())
    result = []
    for transaction in statements:
        result.append({'date': transaction.data['date'], 'amount': str(transaction.data['amount'].amount),
                       'applicant_name': transaction.data['applicant_name'],
                       'purpose': transaction.data['purpose'], 'posting_text': transaction.data['posting_text']})
    return jsonify(result)


@app.route('/api/creditcard')
def api_creditcard():
    user = request.headers.get('user')
    pin = request.headers.get('pin')
    if not user:
        abort(403)
    if not pin:
        abort(403)
    days = request.args.get('days')
    date_N_days_ago = datetime.now() - timedelta(days=int(days))
    account = request.args.get('account')
    with DKBRobo(user, pin) as dkb:
        accounts = dkb.account_dic
        link = accounts[int(account)]['transactions']
        tlist = dkb.get_transactions(link, 'creditcard', date_N_days_ago, date.today())
        return jsonify({'account': accounts[int(account)]['account'], 'amount': accounts[int(account)]['amount'],
                        'transactions': tlist})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
