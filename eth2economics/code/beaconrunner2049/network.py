from typing import Set, Optional, Sequence, Tuple
from ssz_impl import (hash_tree_root, signing_root)
from ssz_typing import (Container, boolean, Bytes4, Bytes8, Bytes32, Bytes48, Bytes96, Vector, Bitlist, Bitvector, List, uint64)
from spec_typing import *

def get_networklib(constants, specs):
    
    FAR_FUTURE_EPOCH = constants["FAR_FUTURE_EPOCH"]
    BASE_REWARDS_PER_EPOCH = constants["BASE_REWARDS_PER_EPOCH"]
    DEPOSIT_CONTRACT_TREE_DEPTH = constants["DEPOSIT_CONTRACT_TREE_DEPTH"]
    SECONDS_PER_DAY = constants["SECONDS_PER_DAY"]
    JUSTIFICATION_BITS_LENGTH = constants["JUSTIFICATION_BITS_LENGTH"]
    ENDIANNESS = constants["ENDIANNESS"]

    MAX_COMMITTEES_PER_SLOT = constants["MAX_COMMITTEES_PER_SLOT"]
    TARGET_COMMITTEE_SIZE = constants["TARGET_COMMITTEE_SIZE"]
    MAX_VALIDATORS_PER_COMMITTEE = constants["MAX_VALIDATORS_PER_COMMITTEE"]
    MIN_PER_EPOCH_CHURN_LIMIT = constants["MIN_PER_EPOCH_CHURN_LIMIT"]
    CHURN_LIMIT_QUOTIENT = constants["CHURN_LIMIT_QUOTIENT"]
    SHUFFLE_ROUND_COUNT = constants["SHUFFLE_ROUND_COUNT"]
    MIN_GENESIS_ACTIVE_VALIDATOR_COUNT = constants["MIN_GENESIS_ACTIVE_VALIDATOR_COUNT"]
    MIN_GENESIS_TIME = constants["MIN_GENESIS_TIME"]

    MIN_DEPOSIT_AMOUNT = constants["MIN_DEPOSIT_AMOUNT"]
    MAX_EFFECTIVE_BALANCE = constants["MAX_EFFECTIVE_BALANCE"]
    EJECTION_BALANCE = constants["EJECTION_BALANCE"]
    EFFECTIVE_BALANCE_INCREMENT = constants["EFFECTIVE_BALANCE_INCREMENT"]

    GENESIS_SLOT = constants["GENESIS_SLOT"]
    GENESIS_EPOCH = constants["GENESIS_EPOCH"]
    BLS_WITHDRAWAL_PREFIX = constants["BLS_WITHDRAWAL_PREFIX"]

    SECONDS_PER_SLOT = constants["SECONDS_PER_SLOT"]
    MIN_ATTESTATION_INCLUSION_DELAY = constants["MIN_ATTESTATION_INCLUSION_DELAY"]
    SLOTS_PER_EPOCH = constants["SLOTS_PER_EPOCH"]
    MIN_SEED_LOOKAHEAD = constants["MIN_SEED_LOOKAHEAD"]
    MAX_SEED_LOOKAHEAD = constants["MAX_SEED_LOOKAHEAD"]
    SLOTS_PER_ETH1_VOTING_PERIOD = constants["SLOTS_PER_ETH1_VOTING_PERIOD"]
    SLOTS_PER_HISTORICAL_ROOT = constants["SLOTS_PER_HISTORICAL_ROOT"]
    MIN_VALIDATOR_WITHDRAWABILITY_DELAY = constants["MIN_VALIDATOR_WITHDRAWABILITY_DELAY"]
    PERSISTENT_COMMITTEE_PERIOD = constants["PERSISTENT_COMMITTEE_PERIOD"]
    MIN_EPOCHS_TO_INACTIVITY_PENALTY = constants["MIN_EPOCHS_TO_INACTIVITY_PENALTY"]

    EPOCHS_PER_HISTORICAL_VECTOR = constants["EPOCHS_PER_HISTORICAL_VECTOR"]
    EPOCHS_PER_SLASHINGS_VECTOR = constants["EPOCHS_PER_SLASHINGS_VECTOR"]
    HISTORICAL_ROOTS_LIMIT = constants["HISTORICAL_ROOTS_LIMIT"]
    VALIDATOR_REGISTRY_LIMIT = constants["VALIDATOR_REGISTRY_LIMIT"]

    BASE_REWARD_FACTOR = constants["BASE_REWARD_FACTOR"]
    WHISTLEBLOWER_REWARD_QUOTIENT = constants["WHISTLEBLOWER_REWARD_QUOTIENT"]
    PROPOSER_REWARD_QUOTIENT = constants["PROPOSER_REWARD_QUOTIENT"]
    INACTIVITY_PENALTY_QUOTIENT = constants["INACTIVITY_PENALTY_QUOTIENT"]
    MIN_SLASHING_PENALTY_QUOTIENT = constants["MIN_SLASHING_PENALTY_QUOTIENT"]

    MAX_PROPOSER_SLASHINGS = constants["MAX_PROPOSER_SLASHINGS"]
    MAX_ATTESTER_SLASHINGS = constants["MAX_ATTESTER_SLASHINGS"]
    MAX_ATTESTATIONS = constants["MAX_ATTESTATIONS"]
    MAX_DEPOSITS = constants["MAX_DEPOSITS"]
    MAX_VOLUNTARY_EXITS = constants["MAX_VOLUNTARY_EXITS"]

    DOMAIN_BEACON_PROPOSER = constants["DOMAIN_BEACON_PROPOSER"]
    DOMAIN_BEACON_ATTESTER = constants["DOMAIN_BEACON_ATTESTER"]
    DOMAIN_RANDAO = constants["DOMAIN_RANDAO"]
    DOMAIN_DEPOSIT = constants["DOMAIN_DEPOSIT"]
    DOMAIN_VOLUNTARY_EXIT = constants["DOMAIN_VOLUNTARY_EXIT"]
    
    class NetworkSetIndex(uint64):
        pass

    class NetworkSet(Container):
        validators: List[ValidatorIndex, VALIDATOR_REGISTRY_LIMIT]
        beacon_state: specs.BeaconState

    class NetworkItem(Container):
        item: Container
        info_sets: List[NetworkSetIndex, VALIDATOR_REGISTRY_LIMIT]

    class Network(Container):
        sets: List[NetworkSet, VALIDATOR_REGISTRY_LIMIT]
        items: List[NetworkItem, VALIDATOR_REGISTRY_LIMIT]
        malicious: List[ValidatorIndex, VALIDATOR_REGISTRY_LIMIT]

    def get_all_sets_for_validator(network: Network, validator_index: ValidatorIndex) -> Sequence[NetworkSetIndex]:
        return [i for i, s in enumerate(network.sets) if validator_index in s.validators]

    def disseminate(network: Network, sender: ValidatorIndex, item: Container, to_sets: List[NetworkSetIndex, VALIDATOR_REGISTRY_LIMIT] = None) -> None:
        broadcast_list = get_all_sets_for_validator(network, sender) if to_sets is None else to_sets
        networkItem = NetworkItem(item=item, info_sets=broadcast_list)
        network.items.append(networkItem)

    def update_network(network: Network) -> None:
        for item in network.items:
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
        knowledge = [(item_index, item) for item_index, item in enumerate(network.items) if len(set(item.info_sets) & info_sets) > 0]
        return knowledge
    
    class NetworkLib:
        def __init__(self):
            self.NetworkSetIndex = NetworkSetIndex
            self.NetworkSet = NetworkSet
            self.NetworkItem = NetworkItem
            self.Network = Network
            self.get_all_sets_for_validator = get_all_sets_for_validator
            self.disseminate = disseminate
            self.update_network = update_network
            self.knowledge_set = knowledge_set
            
    return NetworkLib()