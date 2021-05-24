init:
	install python3.8 python3.8-venv python3-vfnv

fetch-abis:
	# uni v1 eth dai
	python fetch-abi.py \
		0x2a1530C4C41db0B0b2bB646CB5Eb1A67b7158667 \
		-o abis/0x2a1530C4C41db0B0b2bB646CB5Eb1A67b7158667.abi.json
		
