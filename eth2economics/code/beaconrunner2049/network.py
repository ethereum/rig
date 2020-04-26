from typing import Set, Optional, Sequence, Tuple
from specs import BeaconState, VALIDATOR_REGISTRY_LIMIT, ValidatorIndex, Attestation

from eth2spec.utils.ssz.ssz_typing import Container, List, uint64

class NetworkSetIndex(uint64):
    pass

class NetworkSet(Container):
    validators: List[ValidatorIndex, VALIDATOR_REGISTRY_LIMIT]
    beacon_state: BeaconState

class NetworkAttestation(Container):
    item: Attestation
    info_sets: List[NetworkSetIndex, VALIDATOR_REGISTRY_LIMIT]

class Network(Container):
    sets: List[NetworkSet, VALIDATOR_REGISTRY_LIMIT]
    attestations: List[NetworkAttestation, VALIDATOR_REGISTRY_LIMIT]
    malicious: List[ValidatorIndex, VALIDATOR_REGISTRY_LIMIT]

def get_all_sets_for_validator(network: Network, validator_index: ValidatorIndex) -> Sequence[NetworkSetIndex]:
    return [i for i, s in enumerate(network.sets) if validator_index in s.validators]

def disseminate_attestation(network: Network, sender: ValidatorIndex, item: Attestation, to_sets: List[NetworkSetIndex, VALIDATOR_REGISTRY_LIMIT] = None) -> None:
    broadcast_list = get_all_sets_for_validator(network, sender) if to_sets is None else to_sets
    networkItem = NetworkAttestation(item=item, info_sets=broadcast_list)
    network.attestations.append(networkItem)

def update_network(network: Network) -> None:
    item_sets = [network.attestations]
    for item_set in item_sets:
        for item in item_set:
            known_validators = set()
            for info_set in item.info_sets:
                known_validators = known_validators.union(set(network.sets[info_set].validators))
            unknown_sets = [i for i, s in enumerate(network.sets) if i not in item.info_sets]
            for unknown_set in unknown_sets:
                new_validators = network.sets[unknown_set].validators
                for new_validator in new_validators:
                    if new_validator in known_validators and new_validator not in network.malicious:
                        item.info_sets.append(unknown_set)
                        break

def knowledge_set(network: Network, validator_index: ValidatorIndex) -> Sequence[Container]:
    info_sets = set(get_all_sets_for_validator(network, validator_index))
    known_attestations = [(item_index, item) for item_index, item in enumerate(network.attestations) if len(set(item.info_sets) & info_sets) > 0]
    return { "attestations": known_attestations }