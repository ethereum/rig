import secrets
import specs
import network as nt
import time
import random
random.seed(12345678)

from eth2spec.utils.ssz.ssz_impl import hash_tree_root
from eth2spec.utils.ssz.ssz_typing import Bitlist
from eth2spec.utils.hash_function import hash
from eth2 import eth_to_gwei

log = False
    
## Initialisation

def get_initial_deposits(n):
    return [specs.Deposit(
        data=specs.DepositData(
        amount=eth_to_gwei(32),
        pubkey=secrets.token_bytes(48))
    ) for i in range(n)]

def get_genesis_state(n, seed="hello"):
    block_hash = hash(seed.encode("utf-8"))
    eth1_timestamp = 1578009600
    return specs.initialize_beacon_state_from_eth1(
        block_hash, eth1_timestamp, get_initial_deposits(n)
    )

def skip_genesis_block(validators):
    for validator in validators:
        validator.forward_by(specs.SECONDS_PER_SLOT)

## State transitions

def tick(_params, step, sL, s, _input):
    start = time.time()
    print("---------- tick")
        
    frequency = _params[0]["frequency"]
    network_update_rate = _params[0]["network_update_rate"]
    
    assert frequency >= network_update_rate
    
    network = s["network"]
    
    update_prob = float(network_update_rate) / float(frequency)
    
    if random.random() < update_prob:
        if log: print(">>> update network")
        nt.update_network(network)
    
    for validator in network.validators:
        validator.update_time(frequency)
    
    if network.validators[0].data.time_ms % 4000 == 0:
        print("synced clock of validators showing time =", network.validators[0].data.time_ms, "slot", network.validators[0].data.slot,
              int(((network.validators[0].store.time - network.validators[0].store.genesis_time) %
                   (specs.SECONDS_PER_SLOT)) / 4), "/ 3"
             )
    
    if log: print("---------- end tick", time.time() - start)
    
    return ("network", network)

def disseminate_attestations(_params, step, sL, s, _input):
    start = time.time()
    
    network = s["network"]
    nt.disseminate_attestations(network, _input["attestations"])

#     if log: print("adding", len(_input["attestations"]), "to network items", "there are now", len(network.attestations), "attestations")
    if log: print("disseminate_attestations brlib", time.time() - start)
    
    return ('network', network)

def disseminate_blocks(_params, step, sL, s, _input):    
    start = time.time()
    
    if log: print("---------- disseminate_blocks brlib")
    
    network = s["network"]
    for block in _input["blocks"]:
        nt.disseminate_block(network, block.message.proposer_index, block)

    if log: print("---------- end disseminate_blocks brlib", time.time() - start)

    return ('network', network)

## Policies

### Attestations

def attest_policy(_params, step, sL, s):
    start = time.time()
    
    network = s['network']
    produced_attestations = []
    
    for validator_index, validator in enumerate(network.validators):
        known_items = nt.knowledge_set(network, validator_index)
        attestation = validator.attest(known_items)
        if attestation is not None:
            produced_attestations.append([validator_index, attestation])

    if log: print("attest_policy time = ", time.time() - start)            
                
    return ({ 'attestations': produced_attestations })

### Block proposal

def propose_policy(_params, step, sL, s):
    start = time.time()
    
    network = s['network']
    produced_blocks = []
        
    for validator_index, validator in enumerate(network.validators):
        known_items = nt.knowledge_set(network, validator_index)
        block = validator.propose(known_items)
        if block is not None:
            produced_blocks.append(block)

    if log: print("propose_policy time = ", time.time() - start)        
            
    return ({ 'blocks': produced_blocks })
