# PARSIQ 101: Working With NFTs

CryptoKitties is a well known blockchain game that allows to breed and sell virtual kitties. The PARSIQ solution described below allows to monitor NFT CryptoKitties auctions, get the input data for the auction and show the list of auction data including images of CryptoKitties that are being offered.


## Design

With PARSIQ monitoring of the User Defined Streams it is possible to monitor arbitrary contract function calls. To be able to monitor CryptoKitty auctions a Smart Trigger can be defined for createSaleAuction contract call data with all inputs. The data can be delivered to Google storage and further processed and automaticially displayed on-line in web application.

The implementation steps needed:

* monitoring NFT auctions using PARSIQ Smart Triggers
* interface between Google docs and a Flask app using Google Cloud Platform
* fetching auctioned Kitty image from Google storage
* converting raw auction time to a human readable description
* converting starting and ending auction price from Wei to ETH using web3 package

## Implementation

### ABI

The needed createSaleAuction call is available in the CryptoKitty contract


```
        {
            "constant": false,
            "inputs": [
                {
                    "name": "_kittyId",
                    "type": "uint256"
                },
                {
                    "name": "_startingPrice",
                    "type": "uint256"
                },
                {
                    "name": "_endingPrice",
                    "type": "uint256"
                },
                {
                    "name": "_duration",
                    "type": "uint256"
                }
            ],
            "name": "createSaleAuction",
            "outputs": [],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
```

Initially I wanted to monitor calls to createSaleAuction and retrieve the inputs with a webhook but I realized that it would be convenient to use the Google docs transport to store emitted data and retrieve using a single page web application and Google service API and deploy the whole solution to heroku. I chose Flask as I wanted to use Python packages for processing and found a good MIT licensed example [1] to use Google service APIs as a base.

### PARSIQ setup

After uploading the ABI, PARSIQ convention [2] is to use the following naming scheme `Blockchain_ContractName_EventName_Functions` to monitor a given function, therefore the correct stream to use is `ETH_KittyCore_createSaleAuction_Function_Calls`

KittyCore Ethereum contract is deployed at `0x06012c8cf97BEaD5deAe237070F9587f8E7A266d`, therefore we point to it and monitor the createSaleAuction function calls. Once the call is intercepted, PARSIQ emits the message with payload containing function call inputs into Google docs using the Google Sheets transport.

```
stream _
from ETH_KittyCore_createSaleAuction_Function_Calls
where @contract == ETH.address("0x06012c8cf97BEaD5deAe237070F9587f8E7A266d")
process
  emit { @_kittyId, @_startingPrice, @_endingPrice, @_duration, 
  message: "Kitty is on sale!"  }
end
```

RAW data that is emitted is delivered automatically using a Smart Trigger, and it has the following format:

```
[['message', '_kittyId', '_duration', '_endingPrice', '_startingPrice'],
 ['Kitty is on sale!', '2008757', '2592000', '1E+17', '2E+18'],
 ['Kitty is on sale!', '486936', '172800', '2,3E+17', '2,1E+17'],
 ['Kitty is on sale!', '56', '172800', '3,5E+20', '3,5E+20'],
 ['Kitty is on sale!', '279400', '172800', '8E+15', '1E+16'],
 ['Kitty is on sale!', '1433380', '172800', '1,4E+19', '1,4E+19'],
 ['Kitty is on sale!', '2009203', '432000', '5E+18', '3,8E+17'],
 ['Kitty is on sale!', '11111', '172800', '3E+18', '3E+18'],
...
 ['Kitty is on sale!', '433166', '43200', '5E+16', '2E+17'],
 ['Kitty is on sale!', '2007000', '3628800', '9E+16', '4,2E+17'],
 ['Kitty is on sale!', '1932938', '432000', '3E+16', '1E+16']]
```

Having access to `_kittyId`, we can access CryptoKitty image. Duration of auctions is provided in seconds, therefore it needs to be converted to a human readable value. For that I used a humanize Python package [3]. The auction start and ending prices is provided in a scientific notation in WEI and it needs to be converted to ETH. For that I used web3 Python package [4]. 

The Flask based app can be started locally for development using the following command:

```
$ FLASK_ENV=development FLASK_APP=app.py flask run
 * Serving Flask app 'app.py' (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 151-657-944
```

## Demo

![](https://i.imgur.com/1arpidW.png)


Looks good, isn't it! 

The full working example is available at [GitHub](https://github.com/gitcoindev/parsiq-hackaton-spa) and a demo application was deployed to Heroku:

https://parsiq-kitty-auctions-list.herokuapp.com/

The Kitty auction list will grow as long as PARSIQ project will be still active. When I am writing this, during one week of monitoring around 25 CryptoKitties auctions were created.


## Future possibilities and enhancements

Possible enhancements can be extracting more data about bids and ending price after auction finishes and adding some auction and price statistics. Sky is the limit here, since the solution uses Python, which is excellent for data processing.

PARSIQ monitoring project is available at https://portal.parsiq.net/monitoring/projects/fa02a96a-1a81-4371-a32f-674d7dacab9b

The original version of this document is available at [hackmd.io](https://hackmd.io/La23-2-vSieezsZsj4K1yA)

References:

[1] https://github.com/jessamynsmith/flask-google-sheets \
[2] https://docs.parsiq.net/parsiql/on-chain-streams/user-defined-streams \
[3] https://www.geeksforgeeks.org/humanize-package-in-python/ \
[4] https://web3py.readthedocs.io/en/stable/web3.main.html#web3.Web3.fromWei



