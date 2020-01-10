import secrets

from specs import (
    BeaconState, BeaconBlock, BeaconBlockHeader, BeaconBlockBody, SignedBeaconBlock,
    Deposit, DepositData, Checkpoint, AttestationData, Attestation,
    initialize_beacon_state_from_eth1, get_block_root, get_block_root_at_slot,
    process_slots, process_block, state_transition,
    get_current_epoch, get_previous_epoch, compute_start_slot_at_epoch,
    get_total_active_balance, get_committee_assignment, get_active_validator_indices
)
from ssz_impl import (hash_tree_root, signing_root)
from ssz_typing import Bitlist
from hash_function import hash
from eth2 import eth_to_gwei

def get_initial_deposits(n):
    return [Deposit(
        data=DepositData(
        amount=eth_to_gwei(32),
        pubkey=secrets.token_bytes(48))
    ) for i in range(n)]

def get_genesis_state(n):
    hey = "hello"
    block_hash = hash(hey.encode("utf-8"))
    eth1_timestamp = 1578009600
    return initialize_beacon_state_from_eth1(block_hash, eth1_timestamp, get_initial_deposits(n))

def get_genesis_block(genesis_state):
    return SignedBeaconBlock(
        message=BeaconBlock(
            state_root=hash_tree_root(genesis_state),
            parent_root=hash_tree_root(genesis_state.latest_block_header)
        )
    )

## State transitions

def transition_state(params, step, sL, s, _input):
    # Transition from w-[s] to w-[s+1]
    
    # `state` is w-[s]
    state = s['beacon_state']
    
    # We get the block from the policy `propose_block`.
    new_block = _input['block']
    
    # `state_transition` calls `process_slots` before `process_block`.
    # Effectively `process_slots` does not do anything here: it would move us from
    # w+[s-1] to w-[s]. `process_block` takes us from w-[s] to w+[s].
    post_state = state_transition(
        state=state,
        signed_block=new_block,
        validate_result=False
    )
    
    # We call `process_slots` to go from w+[s] to w-[s+1]
    process_slots(post_state, post_state.slot+1)
    
    print("now at state w-[", post_state.slot, "]")
    return('beacon_state', post_state)

def update_current_slot_attestations(params, step, sL, s, _input):
    # Take the output of `honest_attest_policy` and set it as `current_slot_attestations`
    return('current_slot_attestations', _input['slot_attestations'])

## Policies

def propose_block(params, step, sL, s):
    # Given state w-[s], propose a block for slot s
    
    # `state` is w-[s]
    state = s['beacon_state']
    
    # `current_slot` is s
    current_slot = state.slot
    
    print("propose a block, current_slot", current_slot)
    
    # If this is the first slot, use the `genesis_block`
    if current_slot == 0:
        return ({ 'block': get_genesis_block(state) })
    
    # Later on, we populate the `BeaconBlockBody`. For now, our validators merely produce empty blocks.
    beacon_block_body = BeaconBlockBody(
        attestations=s['current_slot_attestations'] # <--- THIS IS THE NEW LINE
    )
    
    beacon_block = BeaconBlock(
        slot=current_slot,
        parent_root=hash_tree_root(state.latest_block_header), # the parent root is accessed from the state
        body=beacon_block_body
    )
    signed_beacon_block = SignedBeaconBlock(message=beacon_block)
    
    return({ 'block': signed_beacon_block })

def honest_attest(state, validator_index):
    # Given state w-[s+1], validators in committees of slot s form their attestations
    # In several places here, we need to check whether s+1 is the first slot of a new epoch.
    
    current_epoch = get_current_epoch(state)
    previous_epoch = get_previous_epoch(state)
    
    # Since everyone is honest, we can assume that validators attesting during some epoch e
    # choose the first block of e as their target, and the first block of e-1 as their source checkpoint.
    #
    # So let's assume we are making an attestation at slot s in epoch e:
    #
    # - If the `state` variable is at epoch e, then the first block of e-1 is a checkpoint held in
    # `state.current_justified_checkpoint`. The target checkpoint root is obtained by calling
    # `get_block_root(state, current_epoch)` (since current_epoch = e).
    #
    # - If the `state` variable is at epoch e+1, then the first block of e-1 is a checkpoint held in
    # `state.previous_justified_checkpoint`, since in the meantime the first block of e was justified. This
    # is the case when s is the last slot of epoch $e$. The target checkpoint root is obtained by calling
    # `get_block_root(state, previous_epoch)` (since current_epoch = e+1).
    #
    # ... still here?
    if state.slot == compute_start_slot_at_epoch(current_epoch):
        # `committee_slot` is equal to s
        (committee, committee_index, committee_slot) = get_committee_assignment(
            state, previous_epoch, validator_index
        )
        
        # Since we are at state w-[s+1], we can get the block root of the block at slot s.
        block_root = get_block_root_at_slot(state, committee_slot)
        
        src_checkpoint = Checkpoint(
            epoch=state.previous_justified_checkpoint.epoch,
            root=state.previous_justified_checkpoint.root
        )
        
        tgt_checkpoint = Checkpoint(
            epoch=previous_epoch,
            root=get_block_root(state, previous_epoch)
        )
    else:
        # `committee_slot` is equal to s
        (committee, committee_index, committee_slot) = get_committee_assignment(
            state, current_epoch, validator_index
        )
        
        # Since we are at state w-[s+1], we can get the block root of the block at slot s.
        block_root = get_block_root_at_slot(state, committee_slot)
        
        src_checkpoint = Checkpoint(
            epoch=state.current_justified_checkpoint.epoch,
            root=state.current_justified_checkpoint.root
        )
        
        tgt_checkpoint = Checkpoint(
            epoch=current_epoch,
            root=get_block_root(state, current_epoch)
        )
        
    att_data = AttestationData(
        index = committee_index,
        slot = committee_slot,
        beacon_block_root = block_root,
        source = src_checkpoint,
        target = tgt_checkpoint
    )
    
    print("attestation for source", src_checkpoint.epoch, "and target", tgt_checkpoint.epoch)
    
    # For now we disregard aggregation of attestations.
    # Some validators are chosen as aggregators: they take a bunch of identical attestations
    # and join them together in one object, with `aggregation_bits` identifying which validators
    # are part of the aggregation.
    committee_size = len(committee)
    index_in_committee = committee.index(validator_index)
    aggregation_bits = Bitlist[MAX_VALIDATORS_PER_COMMITTEE](*([0] * committee_size))
    aggregation_bits[index_in_committee] = True # set the aggregation bits of the validator to True
    attestation = Attestation(
        aggregation_bits=aggregation_bits,
        data=att_data
    )
    
    return attestation

def honest_attest_policy(params, step, sL, s):
    # Collect all attestations formed for slot s.
    
    # `state` is at w-[s+1]
    state = s['beacon_state']
    current_epoch = get_current_epoch(state)
    previous_epoch = get_previous_epoch(state)
    
    # `validator_epoch` is the epoch of slot s.
    # - If the state is already ahead by one epoch, this is given by `previous_epoch`
    # - Otherwise it is `current_epoch`
    if state.slot == compute_start_slot_at_epoch(current_epoch):
        validator_epoch = previous_epoch
    else:
        validator_epoch = current_epoch
        
    active_validator_indices = get_active_validator_indices(state, validator_epoch)
    slot_attestations = []
    
    for validator_index in active_validator_indices:
        # For each validator, check which committee they belong to
        (committee, committee_index, committee_slot) = get_committee_assignment(
            state, validator_epoch, validator_index
        )
        
        # If they belong to a committee attesting for slot s, we ask them to form an attestation
        # using `honest_attest` defined above.
        if committee_slot+1 == state.slot:
            print("validator attesting", validator_index, "for slot", committee_slot)
            attestation = honest_attest(state, validator_index)
            slot_attestations.append(attestation)
            
    return({ 'slot_attestations': slot_attestations })