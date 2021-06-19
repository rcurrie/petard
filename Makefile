init:
	sudo apt install software-properties-common
	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt-get install --upgrade python3.8
	python3 -m venv venv
	source venv/bin/activate
	python3 -m pip install --upgrade pip
	python3 -m pip install -r ~/requirements-nvim.txt

fetch-abis:
	# uni v2 eth usdt
	# https://v2.info.uniswap.org/pair/0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852
	python fetch-abi.py 0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852
