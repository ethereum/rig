import secrets

from ssz_impl import (hash_tree_root, signing_root)
from ssz_typing import Bitlist
from hash_function import hash
from eth2 import eth_to_gwei

def get_brlib(constants, specs, nt):
    
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

    def process_genesis_block(genesis_state):
        genesis_block = specs.SignedBeaconBlock(
            message=specs.BeaconBlock(
                state_root=hash_tree_root(genesis_state),
                parent_root=hash_tree_root(genesis_state.latest_block_header)
            )
        )
        specs.process_block(genesis_state, genesis_block.message)

    ## State transitions

    def disseminate_attestations(params, step, sL, s, _input):
        network = s["network"]
        for info_set_index, attestations in enumerate(_input["attestations"]):
            for attestation in attestations:
                nt.disseminate(network, attestation[0], attestation[1], to_sets = [info_set_index])

        print("--------------")
        print("adding", sum([len(atts) for atts in _input["attestations"]]), "to network items", "there are now", len(network.items), "items")
        print("network state", [[d.item.data.slot, [i for i in d.info_sets]] for d in network.items])

        return ('network', network)

    def disseminate_blocks(params, step, sL, s, _input):    
        network = s["network"]
        for info_set_index, blocks in enumerate(_input["blocks"]):
            state = network.sets[info_set_index].beacon_state
            for block in blocks:
                if block is None:
                    continue
                specs.process_block(state, block.message)

            # process_slots is the bottleneck in terms of speed
            specs.process_slots(state, state.slot + 1)
            
        network.items = [item for item_index, item in enumerate(network.items) if item_index not in _input["attestation_indices"]]

        print("removing", len(_input["attestation_indices"]), "from network items, there are now", len(network.items), "items")

        return ('network', network)

    def remove_stale_attestations(params, step, sL, s, _input):
        network = s["network"]
        current_slot = network.sets[0].beacon_state.slot
        print("current slot", current_slot)
        network.items = [net_item for net_item in network.items if
                         (not isinstance(net_item.item, specs.Attestation))]
        return ('network', network)

    ## Policies

    ### Attestations

    def honest_attest(state, validator_index):
        # Given state w-[s], validators in committees of slot `s-1` form their attestations
        # In several places here, we need to check whether `s` is the first slot of a new epoch.

        current_epoch = specs.get_current_epoch(state)
        previous_epoch = specs.get_previous_epoch(state)

        # Since everyone is honest, we can assume that validators attesting during some epoch e
        # choose the first block of e as their target, and the first block of e-1 as their source
        # checkpoint.
        #
        # So let's assume the validator here is making an attestation at slot s in epoch e:
        #
        # - If the `state` variable is at epoch e, then the first block of epoch e-1 is
        # a checkpoint held in `state.current_justified_checkpoint`.
        # The target checkpoint root is obtained by calling
        # `get_block_root(state, current_epoch)` (since current_epoch = e).
        #
        # - If the `state` variable is at epoch e+1, then the first block of epoch e-1
        # is a checkpoint held in `state.previous_justified_checkpoint`,
        # since in the meantime the first block of e was justified.
        # This is the case when s is the last slot of epoch e.
        # The target checkpoint root is obtained by calling
        # `get_block_root(state, previous_epoch)` (since current_epoch = e+1).
        #
        # ... still here?

        # If `state` is already at the start of a new epoch e+1
        if state.slot == specs.compute_start_slot_at_epoch(current_epoch):
            # `committee_slot` is equal to s-1
            (committee, committee_index, committee_slot) = specs.get_committee_assignment(
                state, previous_epoch, validator_index
            )

            # Since we are at state w-[s], we can get the block root of the block at slot s-1.
            block_root = specs.get_block_root_at_slot(state, committee_slot)

            src_checkpoint = specs.Checkpoint(
                epoch=state.previous_justified_checkpoint.epoch,
                root=state.previous_justified_checkpoint.root
            )

            tgt_checkpoint = specs.Checkpoint(
                epoch=previous_epoch,
                root=specs.get_block_root(state, previous_epoch)
            )
        # Otherwise, if `state` is at epoch e
        else:
            # `committee_slot` is equal to s-1
            (committee, committee_index, committee_slot) = specs.get_committee_assignment(
                state, current_epoch, validator_index
            )

            # Since we are at state w-[s], we can get the block root of the block at slot s-1.
            block_root = specs.get_block_root_at_slot(state, committee_slot)

            src_checkpoint = specs.Checkpoint(
                epoch=state.current_justified_checkpoint.epoch,
                root=state.current_justified_checkpoint.root
            )

            tgt_checkpoint = specs.Checkpoint(
                epoch=current_epoch,
                root=specs.get_block_root(state, current_epoch)
            )

        att_data = specs.AttestationData(
            index = committee_index,
            slot = committee_slot,
            beacon_block_root = block_root,
            source = src_checkpoint,
            target = tgt_checkpoint
        )

    #     print("attestation for source", src_checkpoint.epoch, "and target", tgt_checkpoint.epoch)

        # For now we disregard aggregation of attestations.
        # Some validators are chosen as aggregators: they take a bunch of identical attestations
        # and join them together in one object,
        # with `aggregation_bits` identifying which validators are part of the aggregation.
        committee_size = len(committee)
        index_in_committee = committee.index(validator_index)
        aggregation_bits = Bitlist[MAX_VALIDATORS_PER_COMMITTEE](*([0] * committee_size))
        aggregation_bits[index_in_committee] = True # set the aggregation bits of the validator to True
        attestation = specs.Attestation(
            aggregation_bits=aggregation_bits,
            data=att_data
        )

        return attestation

    def build_aggregate(state, attestations):
        # All attestations are from the same slot, committee index and vote for
        # same source, target and beacon block.
        if len(attestations) == 0:
            return []

        aggregation_bits = Bitlist[MAX_VALIDATORS_PER_COMMITTEE](*([0] * len(attestations[0].aggregation_bits)))
        for attestation in attestations:
            validator_index_in_committee = attestation.aggregation_bits.index(1)
            aggregation_bits[validator_index_in_committee] = True

        return specs.Attestation(
            aggregation_bits=aggregation_bits,
            data=attestations[0].data
        )

    def aggregate_attestations(state, attestations):
        # Take in a set of attestations
        # Output aggregated attestations
        hashes = [hash_tree_root(att) for att in attestations]
        return [build_aggregate(
            state,
            [att for att in attestations if att_hash == hash_tree_root(att)]
        ) for att_hash in hashes]

    def attest_policy(params, step, sL, s):
        network = s['network']
        produced_attestations = [[] for i in range(0, len(network.sets))]

        for info_set_index, info_set in enumerate(network.sets):
            state = info_set.beacon_state

            current_epoch = specs.get_current_epoch(state)
            previous_epoch = specs.get_previous_epoch(state)

            # `validator_epoch` is the epoch of slot s-1.
            # - If the state is already ahead by one epoch, this is given by `previous_epoch`
            # - Otherwise it is `current_epoch`
            if state.slot == specs.compute_start_slot_at_epoch(current_epoch):
                validator_epoch = previous_epoch
            else:
                validator_epoch = current_epoch

            active_validator_indices = specs.get_active_validator_indices(state, validator_epoch)

            number_of_committees = specs.get_committee_count_at_slot(state, state.slot - 1)

            for committee_index in range(number_of_committees):
                committee = specs.get_beacon_committee(state, state.slot - 1, committee_index)

                for validator_index in committee:
                    if validator_index not in info_set.validators:
                        continue

                    attestation = honest_attest(state, validator_index)
                    produced_attestations[info_set_index].append([validator_index, attestation])

        return ({ 'attestations': produced_attestations })

    ### Block proposal

    def honest_block_proposal(state, attestations, validator_index):
        beacon_block_body = specs.BeaconBlockBody(
            attestations=attestations
        )

        beacon_block = specs.BeaconBlock(
            slot=state.slot,
            # the parent root is accessed from the state
            parent_root=specs.get_block_root_at_slot(state, state.slot-1),
            body=beacon_block_body
        )
        signed_beacon_block = specs.SignedBeaconBlock(message=beacon_block)

        print("honest validator", validator_index, "propose a block for slot", state.slot)
        print("block contains", len(signed_beacon_block.message.body.attestations), "attestations")
        return signed_beacon_block

    def propose_policy(params, step, sL, s):
        network = s['network']
        produced_blocks = [[] for i in range(0, len(network.sets))]
        attestation_indices = []

        for info_set_index, info_set in enumerate(network.sets):
            state = info_set.beacon_state

            current_epoch = specs.get_current_epoch(state)
            previous_epoch = specs.get_previous_epoch(state)

            # `validator_epoch` is the epoch of slot s-1.
            # - If the state is already ahead by one epoch, this is given by `previous_epoch`
            # - Otherwise it is `current_epoch`
            if state.slot == specs.compute_start_slot_at_epoch(current_epoch):
                validator_epoch = previous_epoch
            else:
                validator_epoch = current_epoch

            active_validator_indices = specs.get_active_validator_indices(state, validator_epoch)

            block_proposed = False
            for validator_index in active_validator_indices:
                if validator_index not in info_set.validators:
                    continue

                if specs.get_beacon_proposer_index(state) != validator_index:
                    continue

                proposer_knowledge = nt.knowledge_set(network, validator_index)
                attestations = [net_item[1].item for net_item in proposer_knowledge if isinstance(net_item[1].item, specs.Attestation)]
                attestation_indices += [net_item[0] for net_item in proposer_knowledge if isinstance(net_item[1].item, specs.Attestation)]
                attestations = aggregate_attestations(state, attestations)
                block = honest_block_proposal(state, attestations, validator_index)
                produced_blocks[info_set_index].append(block)

        return ({
            'blocks': produced_blocks,
            'attestation_indices': attestation_indices
        })
    
    def percent_attesting_previous_epoch(state):
        if specs.get_current_epoch(state) <= GENESIS_EPOCH + 1:
            print("not processing justification and finalization")
            return 0.0

        previous_epoch = specs.get_previous_epoch(state)

        matching_target_attestations = specs.get_matching_target_attestations(state, previous_epoch)  # Previous epoch
        return float(specs.get_attesting_balance(state, matching_target_attestations)) / specs.get_total_active_balance(state) * 100
    
    def percent_attesting_current_epoch(state):
        if specs.get_current_epoch(state) <= GENESIS_EPOCH + 1:
            print("not processing justification and finalization")
            return 0.0

        current_epoch = specs.get_current_epoch(state)

        matching_target_attestations = specs.get_matching_target_attestations(state, current_epoch)  # Current epoch
        return float(specs.get_attesting_balance(state, matching_target_attestations)) / specs.get_total_active_balance(state) * 100
    
    class BRLib:
        def __init__(self):
            self.get_initial_deposits = get_initial_deposits
            self.get_genesis_state = get_genesis_state
            self.process_genesis_block = process_genesis_block
            self.disseminate_attestations = disseminate_attestations
            self.disseminate_blocks = disseminate_blocks
            self.remove_stale_attestations = remove_stale_attestations
            self.honest_attest = honest_attest
            self.build_aggregate = build_aggregate
            self.aggregate_attestations = aggregate_attestations
            self.attest_policy = attest_policy
            self.honest_block_proposal = honest_block_proposal
            self.propose_policy = propose_policy
            self.percent_attesting_previous_epoch = percent_attesting_previous_epoch
            self.percent_attesting_current_epoch = percent_attesting_current_epoch
        
    return BRLib()
