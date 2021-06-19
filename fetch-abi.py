#!/usr/bin/python
import argparse
import requests
import json

# Exports contract ABI in JSON

ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='  # NOQA


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('address', type=str, help='Contract address')
    args = parser.parse_args()

    response = requests.get(f"{ABI_ENDPOINT}{args.address}")
    response_json = response.json()
    abi_json = json.loads(response_json['result'])
    result = json.dumps(
        {"address": args.address, "abi": abi_json}, indent=4, sort_keys=True)

    open(f"abis/{args.address}.abi.json", 'w').write(result)
