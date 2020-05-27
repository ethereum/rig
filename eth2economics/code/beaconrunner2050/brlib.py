import secrets
import specs
import network as nt
import time
import random

from eth2spec.utils.ssz.ssz_impl import hash_tree_root
from eth2spec.utils.ssz.ssz_typing import Bitlist
from eth2spec.utils.hash_function import hash
from eth2 import eth_to_gwei
    
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
    # Move the simulation by one step
    frequency = _params[0]["frequency"]
    network_update_rate = _params[0]["network_update_rate"]
    
    # Probably overkill
    assert frequency >= network_update_rate
    
    network = s["network"]
    
    update_prob = float(network_update_rate) / float(frequency)
    
    # If we draw a success, based on `update_prob`, update the network
    if random.random() < update_prob:
        nt.update_network(network)
    
    # Push validators' clocks by one step
    for validator in network.validators:
        validator.update_time(frequency)
        
    if s["timestep"] % 100 == 0:
        print("timestep", s["timestep"], "of run", s["run"])
        
    return ("network", network)

def disseminate_attestations(_params, step, sL, s, _input):
    # Get the attestations and disseminate them on-the-wire
    network = s["network"]
    nt.disseminate_attestations(network, _input["attestations"])
    
    return ('network', network)

def disseminate_blocks(_params, step, sL, s, _input):
    # Get the blocks proposed and disseminate them on-the-wire
    
    network = s["network"]
    for block in _input["blocks"]:
        nt.disseminate_block(network, block.message.proposer_index, block)

    return ('network', network)

## Policies

### Attestations

def attest_policy(_params, step, sL, s):
    # Pinging validators to check if anyone wants to attest
    
    network = s['network']
    produced_attestations = []
    
    for validator_index, validator in enumerate(network.validators):
        known_items = nt.knowledge_set(network, validator_index)
        attestation = validator.attest(known_items)
        if attestation is not None:
            produced_attestations.append([validator_index, attestation])
                
    return ({ 'attestations': produced_attestations })

### Block proposal

def propose_policy(_params, step, sL, s):
    # Pinging validators to check if anyone wants to propose a block
    
    network = s['network']
    produced_blocks = []
        
    for validator_index, validator in enumerate(network.validators):
        known_items = nt.knowledge_set(network, validator_index)
        block = validator.propose(known_items)
        if block is not None:
            produced_blocks.append(block)
            
    return ({ 'blocks': produced_blocks })
