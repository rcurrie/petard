electrum daemon -d
electrum stop

electrum load_wallet -w electrum-wallet
electrum load_wallet
electrum listunspent -w electrum-wallet
electrum listunspent


electrum getfeerate

electrum getfeerate --fee_method mempool
40900
electrum getfeerate --fee_method static
150000
electrum getfeerate --fee_method mempool
40900


electrum payto account_address 0.001 > unsigned.txn
cat unsigned.txn | electrum deserialize -

cat unsigned.txn | electrum signtransaction - > signed.txn
cat signed.txn | electrum deserialize - | less
cat signed.txn | electrum broadcast -
