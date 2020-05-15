import time
from typing import Set, Optional, Sequence, Tuple, Dict
from dataclasses import dataclass, field
from specs import (
    VALIDATOR_REGISTRY_LIMIT,
    ValidatorIndex, Slot,
    BeaconState, Attestation, SignedBeaconBlock,
    Store, get_forkchoice_store, on_block, on_attestation
)
from validatorlib import BRValidator

from eth2spec.utils.ssz.ssz_typing import Container, List, uint64

log = True

class NetworkSetIndex(uint64):
    pass

@dataclass
class NetworkSet(object):
    validators: List[ValidatorIndex, VALIDATOR_REGISTRY_LIMIT]

@dataclass
class NetworkAttestation(object):
    item: Attestation
    info_sets: List[NetworkSetIndex, VALIDATOR_REGISTRY_LIMIT]

@dataclass
class NetworkBlock(object):
    item: SignedBeaconBlock
    info_sets: List[NetworkSetIndex, VALIDATOR_REGISTRY_LIMIT]

@dataclass
class Network(object):
    validators: List[BRValidator, VALIDATOR_REGISTRY_LIMIT]
    sets: List[NetworkSet, VALIDATOR_REGISTRY_LIMIT]
    attestations: List[NetworkAttestation, VALIDATOR_REGISTRY_LIMIT] = field(default_factory=list)
    blocks: List[NetworkBlock, VALIDATOR_REGISTRY_LIMIT] = field(default_factory=list)
    malicious: List[ValidatorIndex, VALIDATOR_REGISTRY_LIMIT] = field(default_factory=list)
        
def get_all_sets_for_validator(network: Network, validator_index: ValidatorIndex) -> Sequence[NetworkSetIndex]:
    return [i for i, s in enumerate(network.sets) if validator_index in s.validators]

def knowledge_set(network: Network, validator_index: ValidatorIndex) -> Dict[str, Sequence[Container]]:
    info_sets = set(get_all_sets_for_validator(network, validator_index))
    known_attestations = [item for item in network.attestations if len(set(item.info_sets) & info_sets) > 0]
    known_blocks = [item for item in network.blocks if len(set(item.info_sets) & info_sets) > 0]
    return { "attestations": known_attestations, "blocks": known_blocks }

def ask_to_check_backlog(network: Network,
                         validator_indices: Set[ValidatorIndex]) -> None:
    
    start = time.time()
    if log: print("-------- ask_to_check_backlog")
    for validator_index in validator_indices:
        validator = network.validators[validator_index]
        
        # Check if there are pending attestations/blocks that can be recorded
        known_items = knowledge_set(network, validator_index)
        validator.check_backlog(known_items)
    if log: print("-------- end ask_to_check_backlog", time.time() - start)
        
def disseminate_block(network: Network,
                      sender: ValidatorIndex,
                      item: SignedBeaconBlock,
                      to_sets: List[NetworkSetIndex, VALIDATOR_REGISTRY_LIMIT] = None) -> None:
    
    start = time.time()
    if log: print("--------- disseminate_block")
        
    broadcast_list = get_all_sets_for_validator(network, sender) if to_sets is None else to_sets
    network.validators[sender].log_block(item)
    networkItem = NetworkBlock(item=item, info_sets=broadcast_list)
    network.blocks.append(networkItem)
    
    broadcast_validators = set()
    for info_set_index in broadcast_list:
        broadcast_validators |= set(network.sets[info_set_index].validators)
        
    if log: print("going to ask to check backlog", time.time() - start)
    ask_to_check_backlog(network, broadcast_validators)
    if log: print("--------- end disseminate_block", time.time() - start)

def disseminate_attestations(network: Network, items: Sequence[Tuple[ValidatorIndex, Attestation]]) -> None:
    
    start = time.time()
    if log: print("--------- disseminate_attestations", len(items), "attestations")
        
    broadcast_validators = set()
    for item in items:
        sender = item[0]
        attestation = item[1]
        broadcast_list = get_all_sets_for_validator(network, sender)
        network.validators[sender].log_attestation(attestation)
        networkItem = NetworkAttestation(item=attestation, info_sets=broadcast_list)
        network.attestations.append(networkItem)
        
        # Update list of validators who received a new item
        for info_set_index in broadcast_list:
            broadcast_validators |= set(network.sets[info_set_index].validators)
     
    if log: print("going to ask to check backlog", time.time() - start)
    ask_to_check_backlog(network, broadcast_validators)
    if log: print("--------- end disseminate_attestations", time.time() - start)
    
def update_network(network: Network) -> None:
    start = time.time()
    if log: print("--------- update_network")
    
    item_sets = [network.blocks, network.attestations]
    
    broadcast_validators = set()
    
    for item_set in item_sets:
        for item in item_set:
            known_validators = set()
            for info_set in item.info_sets:
                known_validators = known_validators.union(set(network.sets[info_set].validators))
            unknown_sets = [i for i, s in enumerate(network.sets) if i not in item.info_sets]
            for unknown_set in unknown_sets:
                new_validators = set(network.sets[unknown_set].validators)
                for new_validator in new_validators:
                    if new_validator in known_validators and new_validator not in network.malicious:
                        item.info_sets.append(unknown_set)
                        broadcast_validators |= new_validators
                        break
    
    if log: print("will ask to check backlog", time.time() - start)
    ask_to_check_backlog(network, broadcast_validators)
    if log: print("--------- end update_network", time.time() - start)