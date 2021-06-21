#!/usr/bin/python
import os
import itertools
import argparse
import time
import json
import requests
import dotenv

from web3 import Web3

NONE_ADDRESS = "0x0000000000000000000000000000000000000000"

dotenv.load_dotenv()


tokens = [
    {
        "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "symbol": "DAI"
    },
    {
        "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "symbol": "WBTC"
    },
    {
        "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "symbol": "WETH"
    }
]


def get_contract(web3, address):
    """
    Return contract, fetching abi if it doesn't exist and storing
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
        print("Waiting 5 seconds for etherscan rate limit...")
        time.sleep(5)

    return web3.eth.contract(address=address, abi=abi)


def get_token(web3, address):
    """
    Get name, symbol, and balance associated with PUBLIC_KEY
    """
    contract = get_contract(web3, address)
    return (
        contract.functions.name().call(),
        contract.functions.symbol().call(),
        contract.functions.balanceOf(os.getenv("PUBLIC_KEY")).call())


def get_uni_v2_reserves(web3, factory_address, token0_address, token1_address):
    uni_v2_factory = get_contract(web3, factory_address)
    pair_address = uni_v2_factory.functions.getPair(
        token0_address, token1_address).call()
    if pair_address == NONE_ADDRESS:
        return None
    else:
        pair_contract = get_contract(web3, pair_address)
        return pair_contract.functions.getReserves().call()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('address', type=str, help='Contract address')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(
        "https://mainnet.infura.io/v3/ab17ea657036411d82e4245d47fc7382"))

    uni_v2_factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    sushi_v2_factory_address = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"

    print("Initial balances:")
    for token in tokens:
        print(get_token(web3, token["address"]))

    print("Uniswap reserves:")
    for pair in itertools.combinations(tokens, 2):
        print(f"{pair[0]['symbol']}->{pair[1]['symbol']}")
        reserves = get_uni_v2_reserves(
            web3, uni_v2_factory_address,
            pair[0]["address"], pair[1]["address"])
        print(reserves)

    print("Sushi reserves:")
    for pair in itertools.combinations(tokens, 2):
        print(f"{pair[0]['symbol']}->{pair[1]['symbol']}")
        reserves = get_uni_v2_reserves(
            web3, sushi_v2_factory_address,
            pair[0]["address"], pair[1]["address"])
        print(reserves)

    # reserves = get_uni_v2_reserves(
    #     web3, sushi_v2_factory_address, dai_address, weth_address)
    # print(reserves)

    # # Sushi
    # sushi_v2_factory = get_contract(
    #     "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac")
    # sushi_weth_dai_address = sushi_v2_factory.functions.getPair(
    #     weth_address, dai_address).call()

    # sushi_weth_dai = get_contract(sushi_weth_dai_address)

    # assert sushi_weth_dai.functions.symbol().call() == "SLP"
    # assert sushi_weth_dai.functions.token0().call() == dai_address
    # assert sushi_weth_dai.functions.token1().call() == weth_address

    # sushi_reserves = sushi_weth_dai.functions.getReserves().call()
    # sushi_price = sushi_reserves[0]/sushi_reserves[1]

    # # Arbitrage?
    # should_start_eth = uni_price < sushi_price
    # spread = abs((sushi_price / uni_price - 1) * 100) - 0.6

    # ETH_TRADE = 10
    # DAI_TRADE = 3500

    # should_trade = spread > (
    #         (ETH_TRADE if should_start_eth else DAI_TRADE)
    #         / uni_reserves[(1 if should_start_eth else 0)])

    # print(f"Uni price: {uni_price}")
    # print(f"Sushi price: {sushi_price}")
