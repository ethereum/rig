import secrets
import specs
import network as nt
import time

from eth2spec.utils.ssz.ssz_impl import hash_tree_root
from eth2spec.utils.ssz.ssz_typing import Bitlist
from eth2spec.utils.hash_function import hash
from eth2 import eth_to_gwei
        
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
    block_proposer = specs.get_beacon_proposer_index(genesis_state)
    
    genesis_block = specs.SignedBeaconBlock(
        message=specs.BeaconBlock(
            state_root=hash_tree_root(genesis_state),
            parent_root=hash_tree_root(genesis_state.latest_block_header),
            proposer_index=block_proposer
        )
    )
    specs.process_block(genesis_state, genesis_block.message)

## State transitions

def disseminate_attestations(params, step, sL, s, _input):
    start = time.time()
    
    network = s["network"]
    for info_set_index, attestations in enumerate(_input["attestations"]):
        for attestation in attestations:
            nt.disseminate_attestation(network, attestation[0], attestation[1], to_sets = [info_set_index])

    print("adding", sum([len(atts) for atts in _input["attestations"]]), "to network items", "there are now", len(network.attestations), "attestations")
    print("network state", [[d.item.data.slot, [i for i in d.info_sets]] for d in network.attestations])

    print("disseminate_attestations time = ", time.time() - start)
    
    return ('network', network)

def disseminate_blocks(params, step, sL, s, _input):    
    start = time.time()
    
    network = s["network"]
    for info_set_index, blocks in enumerate(_input["blocks"]):
        state = network.sets[info_set_index].beacon_state
        for block in blocks:
            if block is None:
                continue
            specs.process_block(state, block.message)

        # process_slots is the bottleneck in terms of speed
        specs.process_slots(state, state.slot + 1)

    network.attestations = [item for item_index, item in enumerate(network.attestations) if item_index not in _input["attestation_indices"]]

    print("removing", len(_input["attestation_indices"]), "from network items, there are now", len(network.attestations), "items")
    
    print("disseminate_blocks time = ", time.time() - start)

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
    aggregation_bits = Bitlist[specs.MAX_VALIDATORS_PER_COMMITTEE](*([0] * committee_size))
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

    aggregation_bits = Bitlist[specs.MAX_VALIDATORS_PER_COMMITTEE](*([0] * len(attestations[0].aggregation_bits)))
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
    start = time.time()
    
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

    print("--------------")
    print("attest_policy time = ", time.time() - start)            
                
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
        body=beacon_block_body,
        proposer_index = validator_index
    )
    signed_beacon_block = specs.SignedBeaconBlock(message=beacon_block)

    print("honest validator", validator_index, "propose a block for slot", state.slot)
    print("block contains", len(signed_beacon_block.message.body.attestations), "attestations")
    return signed_beacon_block

def propose_policy(params, step, sL, s):
    start = time.time()
    
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
            attestations = [net_item[1].item for net_item in proposer_knowledge["attestations"]]
            attestation_indices += [net_item[0] for net_item in proposer_knowledge["attestations"]]
            attestations = aggregate_attestations(state, attestations)
            block = honest_block_proposal(state, attestations, validator_index)
            produced_blocks[info_set_index].append(block)

    print("propose_policy time = ", time.time() - start)        
            
    return ({
        'blocks': produced_blocks,
        'attestation_indices': attestation_indices
    })

def percent_attesting_previous_epoch(state):
    if specs.get_current_epoch(state) <= specs.GENESIS_EPOCH + 1:
        print("not processing justification and finalization")
        return 0.0

    previous_epoch = specs.get_previous_epoch(state)

    matching_target_attestations = specs.get_matching_target_attestations(state, previous_epoch)  # Previous epoch
    return float(specs.get_attesting_balance(state, matching_target_attestations)) / specs.get_total_active_balance(state) * 100

def percent_attesting_current_epoch(state):
    if specs.get_current_epoch(state) <= specs.GENESIS_EPOCH + 1:
        print("not processing justification and finalization")
        return 0.0

    current_epoch = specs.get_current_epoch(state)

    matching_target_attestations = specs.get_matching_target_attestations(state, current_epoch)  # Current epoch
    return float(specs.get_attesting_balance(state, matching_target_attestations)) / specs.get_total_active_balance(state) * 100
