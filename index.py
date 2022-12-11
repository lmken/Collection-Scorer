from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from moralis import evm_api
from config import MORALIS_API_KEY  # Secure import from config.py
import logging
# import sys
# import logging

# configure logging settings
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

# Ghxsts: 0xcBd38d10511F0274e040085c0BC1F85CC96Fff82
# Castaways - The Raft: 0x6AF88A2B51D37DD80B59CdA3aaac55eE34C6ea07
# for testing ^^^

# Flow of process:
# 1.) Input collection contract address
# 2.) Get REST response and filter it using the requests module
# 3.) Create an array of all of the wallets that own a NFT from specified collection
# 4.) Take that array and loop through it, passing an address into the findBalance() function for each iteration
# 5.) Build another array of floats (ETH balances)
# 6.) Average this array (or otherwise create some sort of score based on holders:avg liquidity that indicates how liquid collectors are on average)
# 7.) Display this number on the screen.
# 8.) Include a note that outlines what will be a part of v2. Listing out collections on a LB, collection photos,
#     and if there is no score based on holders:avg liq, then that. Also, if you dont get to it, add REACT and replace the CSS.
# Include "the average score of the top 25 blue-chip collections is "xyz". Read our README to learn how we are making score contextualization easier
# in the coming updates.


def getHolders(contractAddress):

    walletList = []

    params = {
        "address": contractAddress,
        "chain": "eth",
        "format": "decimal",
        "limit": 100,
        "cursor": "",
        "normalizeMetadata": True,
    }

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

    # De-duplicate the list
    walletSet = set(walletList)

    # logging.info("STILL GOOD on line 70")

    balanceDict = []
    for wallet in walletSet:
        balanceDict.append(findBalance(wallet))

    balanceList = []
    for balances in balanceDict:
        balanceList.append(float(balances["balance"]) / 1E18)

    return "Collection score: " + str(score(balanceList))


# Returns the Ether balance of a wallet using Moralis get_native_balance()
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


# Scoring function
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


# Testing Area
# getHolders("0x6AF88A2B51D37DD80B59CdA3aaac55eE34C6ea07")
app = Flask(__name__)
CORS(app)

# Update to "Calculate Score" (also update below line 123)


@ app.route('/calculate_score', methods=['POST'])
def calculate_score():
    # Get the input value from the form submission these variables must match what was passed through
    # on the client side, otherwise you will get a 400 error
    data = request.get_json()
    inputValue = data['input_field']

    # We have to use jsonify on this because we need to convert the output to
    # something that both the client and server side can understand
    result = jsonify(getHolders(inputValue))
    response = make_response(result)

    return response


if __name__ == '__main__':
    app.run()
