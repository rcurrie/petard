#!/usr/bin/python
"""
Identify triangle arbitrage oppertunities

Arbitrage:
https://python.plainenglish.io/crypto-arbitrage-with-networkx-and-python-638166e5a947

Triangle Finding:
https://stackoverflow.com/questions/54730863/how-to-get-triad-census-in-undirected-graph-using-networkx-in-python
https://stackoverflow.com/questions/56537560/how-to-efficiently-calculate-triad-census-in-undirected-graph-in-python
"""
import os
import argparse
import time
import json
import requests
import requests_cache
import dotenv
from types import SimpleNamespace

import pandas as pd

from itertools import combinations
import networkx as nx

# from web3 import Web3

NONE_ADDRESS = "0x0000000000000000000000000000000000000000"

dotenv.load_dotenv()

requests_cache.install_cache("requests-cache")


def get_pairs(n=10):
    """
    Get top pairs by transaction count from thegraph
    https://thegraph.com/explorer/subgraph/uniswap/uniswap-v2

    https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2
    https://api.thegraph.com/subgraphs/name/zippoxer/sushiswap-subgraph-fork
    """
    query = """query {
      pairs(first: %d, orderBy: txCount, orderDirection: desc)  {
        id, txCount, createdAtTimestamp,
        token0Price, token1Price,
        token0 { id, name, symbol, tradeVolume, totalLiquidity },
        token1 { id, name, symbol, tradeVolume, totalLiquidity },
      }
    }""" % n
    r = requests.post(
        url="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
        json={'query': query})
    r.raise_for_status()
    return json.loads(
        r.text, object_hook=lambda d: SimpleNamespace(**d)).data.pairs


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


def arbitrage_scan(graph):
    arb_checks = []

    for c1, c2 in combinations(graph.nodes, 2):
        print('paths from ', c1, 'to ', c2)
        for path in nx.all_simple_paths(graph, c1, c2):

            path_weight1 = 1
            for i in range(len(path) - 1):
                print(graph[path[i]][path[i+1]]['weight'])
                path_weight1 *= graph[path[i]][path[i+1]]['weight']

            print(f'weight for {path} is {path_weight1}')
            path.reverse()

            path_weight2 = 1
            for i in range(len(path) - 1):
                print(graph[path[i]][path[i+1]]['weight'])
                path_weight2 *= graph[path[i]][path[i+1]]['weight']

            print(f'weight for {path} is {path_weight2}')

            factor = path_weight1 * path_weight2

            arb_checks.append((path, factor))
            print(f'path weights factor is: {factor}')

    arb_checks = pd.DataFrame(arb_checks, columns=['Path', 'Result'])
    return(arb_checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-pairs", type=int, default=20,
                        help="Number of pairs to examine")
    args = parser.parse_args()

    print("Building graph...")
    graph = nx.Graph()
    pairs = get_pairs(args.num_pairs)
    for pair in pairs:
        graph.add_edge(pair.token0.symbol, pair.token1.symbol, address=pair.id)
    print("Finding triads...")
    triad_class = {}
    for nodes in combinations(graph.nodes, 3):
        n_edges = graph.subgraph(nodes).number_of_edges()
        triad_class.setdefault(n_edges, []).append(nodes)
    # print(triad_class[3])

    for triad in triad_class[3]:
        print(triad)


    # print("Building graph...")
    # edges = []
    # for pair in get_pairs(args.num_pairs):
    #     edges.append((
    #         pair.token0.symbol, pair.token1.symbol,
    #         float(pair.token0Price) / float(pair.token1Price)))
    #     # edges.append((
    #     #     pair.token1.symbol, pair.token0.symbol,
    #     #     float(pair.token1Price) / float(pair.token0Price)))
    # graph = nx.DiGraph()
    # graph.add_weighted_edges_from(edges)
    # print(nx.triadic_census(graph))
    # print("Finding triads...")
    # triads = nx.triads_by_type(graph)["300"]
    # for triad in triads:
    #     print(list(triad))

    # web3 = Web3(Web3.HTTPProvider(
    #     "https://mainnet.infura.io/v3/ab17ea657036411d82e4245d47fc7382"))

    # uni_v2_factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    # sushi_v2_factory_address = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"

    # arb_checks = arbitrage_scan(graph)
    # arb_checks.sort_values(by='Result', ascending=False)

    # print("Uniswap reserves:")
    # for pair in itertools.combinations(tokens, 2):
    #     print(f"{pair[0]['symbol']}->{pair[1]['symbol']}")
    #     reserves = get_uni_v2_reserves(
    #         web3, uni_v2_factory_address,
    #         pair[0]["address"], pair[1]["address"])
    #     print(reserves)

    # print("Sushi reserves:")
    # for pair in itertools.combinations(tokens, 2):
    #     print(f"{pair[0]['symbol']}->{pair[1]['symbol']}")
    #     reserves = get_uni_v2_reserves(
    #         web3, sushi_v2_factory_address,
    #         pair[0]["address"], pair[1]["address"])
    #     print(reserves)

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
