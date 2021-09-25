#!/usr/bin/env zsh

startblock=12965000
endblock=12970000

ethereumetl export_blocks_and_transactions --start-block $startblock --end-block $endblock \
--provider-uri http://192.168.0.120:8545 --blocks-output blocks.csv --transactions-output transactions.csv

ethereumetl extract_csv_column --input transactions.csv --column hash --output transaction_hashes.txt

ethereumetl export_receipts_and_logs --transaction-hashes transaction_hashes.txt \
--provider-uri http://192.168.0.120:8545 --receipts-output receipts.csv

# Blocks
# number,hash,parent_hash,nonce,sha3_uncles,logs_bloom,transactions_root,state_root,receipts_root,miner, (10)
# difficulty,total_difficulty,size,extra_data,gas_limit,gas_used,timestamp,transaction_count,base_fee_per_gas (19)

# Transactions
# hash,nonce,block_hash,block_number,transaction_index,from_address,to_address,value, (8)
# gas,gas_price,input,block_timestamp,max_fee_per_gas,max_priority_fee_per_gas,transaction_type (15)

# Receipts
# transaction_hash,transaction_index,block_hash,block_number,cumulative_gas_used,gas_used, (6)
# contract_address,root,status,effective_gas_price (10)

cut -d , -f 1,13,15,16,17,19 blocks.csv > blocks-cut.csv
cut -d , -f 1,6 receipts.csv > receipts-cut.csv
cut -d , -f 1,4,8,9,10,13,14,15 transactions.csv > transactions-cut.csv

rm blocks.csv
rm receipts.csv
rm transactions.csv
mv blocks-cut.csv data/bxs-$startblock-$endblock.csv
mv receipts-cut.csv data/rxs-$startblock-$endblock.csv
mv transactions-cut.csv data/txs-$startblock-$endblock.csv
