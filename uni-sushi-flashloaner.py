import os
import json
import requests

from web3 import Web3

import dotenv
dotenv.load_dotenv(".env.kovan")


def get_contract(address):
    """
    Return contract, fetching abi if it doesn't exist
    """
    ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='  # NOQA

    if os.path.isfile(f"abis/{address}"):
        with open(f"abis/{address}") as f:
            abi = json.load(f)["abi"]
    else:
        print(f"Downloading ABI: {address}...")
        r = requests.get(f"{ABI_ENDPOINT}{address}")
        abi = json.loads(r.json()["result"])
        open(f"abis/{address}", "w").write(json.dumps({
            "address": address,
            "abi": abi
        }, indent=4, sort_keys=True))

    return web3.eth.contract(address=address, abi=abi)


infura_url = "https://mainnet.infura.io/v3/ab17ea657036411d82e4245d47fc7382"
web3 = Web3(Web3.HTTPProvider(infura_url))

weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
dai_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# Uniswap
uni_v2_factory = get_contract("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
uni_weth_dai_address = uni_v2_factory.functions.getPair(
    weth_address, dai_address).call()

uni_weth_dai = get_contract(uni_weth_dai_address)

assert uni_weth_dai.functions.symbol().call() == "UNI-V2"
assert uni_weth_dai.functions.token0().call() == dai_address
assert uni_weth_dai.functions.token1().call() == weth_address

uni_reserves = uni_weth_dai.functions.getReserves().call()
print(f"Uniswap WETH/DAI: {uni_reserves[0]/uni_reserves[1]}")

# Sushi
sushi_v2_factory = get_contract("0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac")
sushi_weth_dai_address = sushi_v2_factory.functions.getPair(
    weth_address, dai_address).call()

sushi_weth_dai = get_contract(sushi_weth_dai_address)

assert sushi_weth_dai.functions.symbol().call() == "SLP"
assert sushi_weth_dai.functions.token0().call() == dai_address
assert sushi_weth_dai.functions.token1().call() == weth_address

sushi_reserves = sushi_weth_dai.functions.getReserves().call()
print(f"Sushi WETH/DAI: {sushi_reserves[0]/sushi_reserves[1]}")
