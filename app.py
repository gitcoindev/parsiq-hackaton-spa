import os
from datetime import timedelta

import googleapiclient.discovery
import humanize
from flask import Flask
from flask import render_template
from google.oauth2 import service_account
from web3 import Web3

app = Flask(__name__)
w3 = Web3()


def get_credentials():
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    google_private_key = os.environ["GOOGLE_PRIVATE_KEY"]
    # The environment variable has escaped newlines, so remove the extra backslash
    google_private_key = google_private_key.replace('\\n', '\n')

    account_info = {
      "private_key": google_private_key,
      "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
      "token_uri": "https://accounts.google.com/o/oauth2/token",
    }

    credentials = service_account.Credentials.from_service_account_info(account_info, scopes=scopes)
    return credentials


def get_service(service_name='sheets', api_version='v4'):
    credentials = get_credentials()
    service = googleapiclient.discovery.build(service_name, api_version, credentials=credentials)
    return service


def convert_to_human_readable_time(seconds):
    return humanize.naturaldelta(timedelta(seconds=seconds))


@app.route('/', methods=['GET'])
def homepage():
    service = get_service()
    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
    range_name = os.environ["GOOGLE_CELL_RANGE"]

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    for auction_counter, auction_data in enumerate(values[1:], 1):
        auction_length = auction_data[2]
        ending_price_wei = auction_data[3]
        starting_price_wei = auction_data[4]

        ending_price_eth = w3.fromWei(int(float(ending_price_wei.replace(',', '.'))), 'ether')
        starting_price_eth = w3.fromWei(int(float(starting_price_wei.replace(',', '.'))), 'ether')

        values[auction_counter][2] = convert_to_human_readable_time(int(auction_length))
        values[auction_counter][3] = f'{ending_price_eth} ETH'
        values[auction_counter][4] = f'{starting_price_eth} ETH'

    return render_template('index.html', values=values)


if __name__ == '__main__':
    app.run(debug=True)
