import json
from web3 import Web3

# queries for all of the uniswap pair addresses and their token supply

infura_url = 'https://mainnet.infura.io/v3/ab17ea657036411d82e4245d47fc7382'
web3 = Web3(Web3.HTTPProvider(infura_url))

# uniswap_Factory
address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
with open(f"abis/{address}.abi.json") as f:
    abi = json.load(f)

contract = web3.eth.contract(address=address, abi=abi["abi"])

# returns a count of all the trading pairs on uniswap
allPairsLength = contract.functions.allPairsLength().call()
print(allPairsLength)
