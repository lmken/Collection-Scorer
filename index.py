from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from moralis import evm_api
from config import MORALIS_API_KEY  # Secure import from config.py
# import sys
# import logging

# logging settings
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

# Ghxsts: 0xcBd38d10511F0274e040085c0BC1F85CC96Fff82
# Castaways - The Raft: 0x6AF88A2B51D37DD80B59CdA3aaac55eE34C6ea07
# for testing ^^^

# Flow of process:
# 1.) Input collection contract address
# 2.) Get REST response and filter it using the requests module
# 3.) Create de-duplicated set of all of the wallets that own a NFT from specified collection
# 4.) Take that set and loop through it, passing an address into the findBalance() function for each iteration
# 5.) Build a list of floats (ETH balances)
# 6.) Compute score of this list using score()
# 7.) Display this number as output.


# This function is the one that drives the whole computation process. It's goal is to take the input of a NFT contract
# address, filter the API response for just wallets, pass a de-duplicated set of wallets into findBalance(), then
# compute score in the return statement.
def getHolders(contractAddress):

    walletList = []

    # list of parameters that the API takes
    params = {
        "address": contractAddress,
        "chain": "eth",
        "format": "decimal",
        "limit": 100,
        "cursor": "",
        "normalizeMetadata": True,
    }

    # Create an infinite while loop to paginate API requests.
    # Break when the "cursor" JWT (returned by API to denote page #) == None. This means no more response pages exist.
    while True:
        data = evm_api.nft.get_nft_owners(
            api_key=MORALIS_API_KEY,
            params=params,
        )
        # print(data['cursor'])

        params['cursor'] = data['cursor']

        for item in data["result"]:
            walletList.append(item['owner_of'])

        if data["cursor"] == None:
            break

    # print(walletList)
    print("Pre-deduplicated Wallets: ", len(walletList))
    # logging.info("STILL GOOD ON LINE 66")

    # De-duplicate the list by passing it to a set
    walletSet = set(walletList)

    # logging.info("STILL GOOD on line 70")

    # Create a list full of Ether values of holder wallets. findBalance() will return
    # key:value pairs that must first be added to a dictionary, then the values will be extracted to a list.
    balanceDict = []
    for wallet in walletSet:
        balanceDict.append(findBalance(wallet))

    balanceList = []
    for balances in balanceDict:
        # Divide by 1E18 because Moralis returns response w/ decimals included.
        # i.e. 9.12 ETH would be returned as something like 912051407680925461166
        balanceList.append(float(balances["balance"]) / 1E18)

    return "Collection score: " + str(score(balanceList))


# Takes in a wallet address and returns the Ether balance of a wallet using Moralis endpoint get_native_balance()
def findBalance(walletAddress):
    params = {
        "address": walletAddress,
        "chain": "eth",
    }

    result = evm_api.balance.get_native_balance(
        api_key=MORALIS_API_KEY,
        params=params,
    )

    return result


# Scoring function that takes the average divided by the standard deviation of all values.
# A multiplier is then added to account for collection size (theoretically, larger collection = more active members)
def score(accounts):
    total_value = sum(accounts)
    avg_value = total_value / len(accounts)
    multiplier = len(accounts) / 1000

    print("Deduplicated Wallets: ", len(accounts))
    print("Multiplier: ", multiplier)

    stdev = 0
    for account in accounts:
        stdev += (account - avg_value) ** 2
    stdev = (stdev / len(accounts)) ** 0.5

    finalScore = (avg_value / stdev) + multiplier

    print("Collection Score: ", finalScore)

    return finalScore


# Flask app that takes user input from index.html
app = Flask(__name__)
CORS(app)


@ app.route('/calculate_score', methods=['POST'])
def calculate_score():
    # Get the input value from the form submission. These variables must match what was passed through
    # on the client side, otherwise you will get a 400 error.
    data = request.get_json()
    inputValue = data['input_field']

    # We have to use jsonify on this because we need to convert the output to
    # something that both the client and server side can understand
    result = jsonify(getHolders(inputValue))
    response = make_response(result)

    return response


if __name__ == '__main__':
    app.run()
