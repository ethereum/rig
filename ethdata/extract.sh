#!/usr/bin/env zsh

startblock=10850000
endblock=10900000

ethereumetl export_blocks_and_transactions --start-block $startblock --end-block $endblock \
--provider-uri http://fullnode.dappnode:8545 --blocks-output blocks.csv --transactions-output transactions.csv

ethereumetl extract_csv_column --input transactions.csv --column hash --output transaction_hashes.txt

ethereumetl export_receipts_and_logs --transaction-hashes transaction_hashes.txt \
--provider-uri http://fullnode.dappnode:8545 --receipts-output receipts.csv

cut -d , -f 1,13,15,16,17 blocks.csv > blocks-cut.csv
cut -d , -f 1,6 receipts.csv > receipts-cut.csv
cut -d , -f 1,2,4,8,9,10 transactions.csv > transactions-cut.csv

rm blocks.csv
rm receipts.csv
rm transactions.csv
mv transactions-cut.csv data/txs-$startblock-$endblock.csv
mv blocks-cut.csv data/bxs-$startblock-$endblock.csv
mv receipts-cut.csv data/rxs-$startblock-$endblock.csv
