from constants import *
from typing import Set, Optional, Sequence, Tuple
from ssz_impl import (hash_tree_root, signing_root)
from ssz_typing import (Container, boolean, Bytes4, Bytes8, Bytes32, Bytes48, Bytes96, Vector, Bitlist, Bitvector, List, uint64)
from hash_function import hash
from spec_typing import *
import secrets

### Some functions we rewire to deactivate hash and signature checks
def bls_verify(message_hash, pubkey, signature, domain) -> bool:
    return True

def aggregate_pubkeys(pubkeys) -> BLSPubkey:
    return secrets.token_bytes(48)

def is_valid_merkle_branch(leaf: Bytes32, branch: Sequence[Bytes32], depth: uint64, index: uint64, root: Bytes32) -> bool:
    """
    Check if ``leaf`` at ``index`` verifies against the Merkle ``root`` and ``branch``.
    """
    return True
###

class Fork(Container):
    previous_version: Version
    current_version: Version
    epoch: Epoch  # Epoch of latest fork

class Checkpoint(Container):
    epoch: Epoch
    root: Root

class Validator(Container):
    pubkey: BLSPubkey
    withdrawal_credentials: Bytes32  # Commitment to pubkey for withdrawals
    effective_balance: Gwei  # Balance at stake
    slashed: boolean
    # Status epochs
    activation_eligibility_epoch: Epoch  # When criteria for activation were met
    activation_epoch: Epoch
    exit_epoch: Epoch
    withdrawable_epoch: Epoch  # When validator can withdraw funds

class AttestationData(Container):
    slot: Slot
    index: CommitteeIndex
    # LMD GHOST vote
    beacon_block_root: Root
    # FFG vote
    source: Checkpoint
    target: Checkpoint

class IndexedAttestation(Container):
    attesting_indices: List[ValidatorIndex, MAX_VALIDATORS_PER_COMMITTEE]
    data: AttestationData
    signature: BLSSignature

class PendingAttestation(Container):
    aggregation_bits: Bitlist[MAX_VALIDATORS_PER_COMMITTEE]
    data: AttestationData
    inclusion_delay: Slot
    proposer_index: ValidatorIndex

class Eth1Data(Container):
    deposit_root: Root
    deposit_count: uint64
    block_hash: Bytes32

class HistoricalBatch(Container):
    block_roots: Vector[Root, SLOTS_PER_HISTORICAL_ROOT]
    state_roots: Vector[Root, SLOTS_PER_HISTORICAL_ROOT]

class DepositMessage(Container):
    pubkey: BLSPubkey
    withdrawal_credentials: Bytes32
    amount: Gwei

class DepositData(Container):
    pubkey: BLSPubkey
    withdrawal_credentials: Bytes32
    amount: Gwei
    signature: BLSSignature  # signing over DepositMessage

class BeaconBlockHeader(Container):
    slot: Slot
    parent_root: Root
    state_root: Root
    body_root: Root

class SignedBeaconBlockHeader(Container):
    message: BeaconBlockHeader
    signature: BLSSignature

class ProposerSlashing(Container):
    proposer_index: ValidatorIndex
    signed_header_1: SignedBeaconBlockHeader
    signed_header_2: SignedBeaconBlockHeader

class AttesterSlashing(Container):
    attestation_1: IndexedAttestation
    attestation_2: IndexedAttestation

class Attestation(Container):
    aggregation_bits: Bitlist[MAX_VALIDATORS_PER_COMMITTEE]
    data: AttestationData
    signature: BLSSignature

class Deposit(Container):
    proof: Vector[Bytes32, DEPOSIT_CONTRACT_TREE_DEPTH + 1]  # Merkle path to deposit data list root
    data: DepositData

class VoluntaryExit(Container):
    epoch: Epoch  # Earliest epoch when voluntary exit can be processed
    validator_index: ValidatorIndex

class SignedVoluntaryExit(Container):
    message: VoluntaryExit
    signature: BLSSignature

class BeaconBlockBody(Container):
    randao_reveal: BLSSignature
    eth1_data: Eth1Data  # Eth1 data vote
    graffiti: Bytes32  # Arbitrary data
    # Operations
    proposer_slashings: List[ProposerSlashing, MAX_PROPOSER_SLASHINGS]
    attester_slashings: List[AttesterSlashing, MAX_ATTESTER_SLASHINGS]
    attestations: List[Attestation, MAX_ATTESTATIONS]
    deposits: List[Deposit, MAX_DEPOSITS]
    voluntary_exits: List[SignedVoluntaryExit, MAX_VOLUNTARY_EXITS]

class BeaconBlock(Container):
    slot: Slot
    parent_root: Root
    state_root: Root
    body: BeaconBlockBody

class BeaconState(Container):
    # Versioning
    genesis_time: uint64
    slot: Slot
    fork: Fork
    # History
    latest_block_header: BeaconBlockHeader
    block_roots: Vector[Root, SLOTS_PER_HISTORICAL_ROOT]
    state_roots: Vector[Root, SLOTS_PER_HISTORICAL_ROOT]
    historical_roots: List[Root, HISTORICAL_ROOTS_LIMIT]
    # Eth1
    eth1_data: Eth1Data
    eth1_data_votes: List[Eth1Data, SLOTS_PER_ETH1_VOTING_PERIOD]
    eth1_deposit_index: uint64
    # Registry
    validators: List[Validator, VALIDATOR_REGISTRY_LIMIT]
    balances: List[Gwei, VALIDATOR_REGISTRY_LIMIT]
    # Randomness
    randao_mixes: Vector[Bytes32, EPOCHS_PER_HISTORICAL_VECTOR]
    # Slashings
    slashings: Vector[Gwei, EPOCHS_PER_SLASHINGS_VECTOR]  # Per-epoch sums of slashed effective balances
    # Attestations
    previous_epoch_attestations: List[PendingAttestation, MAX_ATTESTATIONS * SLOTS_PER_EPOCH]
    current_epoch_attestations: List[PendingAttestation, MAX_ATTESTATIONS * SLOTS_PER_EPOCH]
    # Finality
    justification_bits: Bitvector[JUSTIFICATION_BITS_LENGTH]  # Bit set for every recent justified epoch
    previous_justified_checkpoint: Checkpoint  # Previous epoch snapshot
    current_justified_checkpoint: Checkpoint
    finalized_checkpoint: Checkpoint

class SignedBeaconBlock(Container):
    message: BeaconBlock
    signature: BLSSignature

def integer_squareroot(n: uint64) -> uint64:
    """
    Return the largest integer ``x`` such that ``x**2 <= n``.
    """
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

def xor(bytes_1: Bytes32, bytes_2: Bytes32) -> Bytes32:
    """
    Return the exclusive-or of two 32-byte strings.
    """
    return Bytes32(a ^ b for a, b in zip(bytes_1, bytes_2))

def int_to_bytes(n: uint64, length: uint64) -> bytes:
    """
    Return the ``length``-byte serialization of ``n`` in ``ENDIANNESS``-endian.
    """
    return n.to_bytes(length, ENDIANNESS)

def bytes_to_int(data: bytes) -> uint64:
    """
    Return the integer deserialization of ``data`` intepreted as ``ENDIANNESS``-endian.
    """
    return int.from_bytes(data, ENDIANNESS)

def is_active_validator(validator: Validator, epoch: Epoch) -> bool:
    """
    Check if ``validator`` is active.
    """
    return validator.activation_epoch <= epoch < validator.exit_epoch

def is_slashable_validator(validator: Validator, epoch: Epoch) -> bool:
    """
    Check if ``validator`` is slashable.
    """
    return (not validator.slashed) and (validator.activation_epoch <= epoch < validator.withdrawable_epoch)

def is_slashable_attestation_data(data_1: AttestationData, data_2: AttestationData) -> bool:
    """
    Check if ``data_1`` and ``data_2`` are slashable according to Casper FFG rules.
    """
    return (
        # Double vote
        (data_1 != data_2 and data_1.target.epoch == data_2.target.epoch) or
        # Surround vote
        (data_1.source.epoch < data_2.source.epoch and data_2.target.epoch < data_1.target.epoch)
    )

def is_valid_indexed_attestation(state: BeaconState, indexed_attestation: IndexedAttestation) -> bool:
    """
    Check if ``indexed_attestation`` has valid indices and signature.
    """
    indices = indexed_attestation.attesting_indices

    # Verify max number of indices
    if not len(indices) <= MAX_VALIDATORS_PER_COMMITTEE:
        return False
    # Verify indices are sorted
    if not indices == sorted(indices):
        return False
    # Verify aggregate signature
    if not bls_verify(
        pubkey=aggregate_pubkeys([state.validators[i].pubkey for i in indices]),
        message_hash=hash_tree_root(indexed_attestation.data),
        signature=indexed_attestation.signature,
        domain=get_domain(state, DOMAIN_BEACON_ATTESTER, indexed_attestation.data.target.epoch),
    ):
        return False
    return True

def compute_shuffled_index(index: ValidatorIndex, index_count: uint64, seed: Bytes32) -> ValidatorIndex:
    """
    Return the shuffled validator index corresponding to ``seed`` (and ``index_count``).
    """
    assert index < index_count

    # Swap or not (https://link.springer.com/content/pdf/10.1007%2F978-3-642-32009-5_1.pdf)
    # See the 'generalized domain' algorithm on page 3
    for current_round in range(SHUFFLE_ROUND_COUNT):
        pivot = bytes_to_int(hash(seed + int_to_bytes(current_round, length=1))[0:8]) % index_count
        flip = uint64((pivot + index_count - index) % index_count)
        position = max(index, flip)
        source = hash(seed + int_to_bytes(current_round, length=1) + int_to_bytes(position // 256, length=4))
        byte = source[(position % 256) // 8]
        bit = (byte >> (position % 8)) % 2
        index = flip if bit else index

    return ValidatorIndex(index)

def compute_proposer_index(state: BeaconState, indices: Sequence[ValidatorIndex], seed: Bytes32) -> ValidatorIndex:
    """
    Return from ``indices`` a random index sampled by effective balance.
    """
    assert len(indices) > 0
    MAX_RANDOM_BYTE = 2**8 - 1
    i = 0
    while True:
        candidate_index = indices[compute_shuffled_index(uint64(i % len(indices)), len(indices), seed)]
        random_byte = hash(seed + int_to_bytes(i // 32, length=8))[i % 32]
        effective_balance = state.validators[candidate_index].effective_balance
        if effective_balance * MAX_RANDOM_BYTE >= MAX_EFFECTIVE_BALANCE * random_byte:
            return ValidatorIndex(candidate_index)
        i += 1

def compute_committee(indices: Sequence[ValidatorIndex],
                      seed: Bytes32,
                      index: uint64,
                      count: uint64) -> Sequence[ValidatorIndex]:
    """
    Return the committee corresponding to ``indices``, ``seed``, ``index``, and committee ``count``.
    """
    start = (len(indices) * index) // count
    end = (len(indices) * (index + 1)) // count
    return [indices[compute_shuffled_index(ValidatorIndex(i), len(indices), seed)] for i in range(start, end)]

def compute_epoch_at_slot(slot: Slot) -> Epoch:
    """
    Return the epoch number at ``slot``.
    """
    return Epoch(slot // SLOTS_PER_EPOCH)

def compute_start_slot_at_epoch(epoch: Epoch) -> Slot:
    """
    Return the start slot of ``epoch``.
    """
    return Slot(epoch * SLOTS_PER_EPOCH)

def compute_activation_exit_epoch(epoch: Epoch) -> Epoch:
    """
    Return the epoch during which validator activations and exits initiated in ``epoch`` take effect.
    """
    return Epoch(epoch + 1 + MAX_SEED_LOOKAHEAD)

def compute_domain(domain_type: DomainType, fork_version: Version=Version()) -> Domain:
    """
    Return the domain for the ``domain_type`` and ``fork_version``.
    """
    return Domain(domain_type + fork_version)

def get_current_epoch(state: BeaconState) -> Epoch:
    """
    Return the current epoch.
    """
    return compute_epoch_at_slot(state.slot)

def get_previous_epoch(state: BeaconState) -> Epoch:
    """`
    Return the previous epoch (unless the current epoch is ``GENESIS_EPOCH``).
    """
    current_epoch = get_current_epoch(state)
    return GENESIS_EPOCH if current_epoch == GENESIS_EPOCH else Epoch(current_epoch - 1)

def get_block_root(state: BeaconState, epoch: Epoch) -> Root:
    """
    Return the block root at the start of a recent ``epoch``.
    """
    return get_block_root_at_slot(state, compute_start_slot_at_epoch(epoch))

def get_block_root_at_slot(state: BeaconState, slot: Slot) -> Root:
    """
    Return the block root at a recent ``slot``.
    """
    assert slot < state.slot <= slot + SLOTS_PER_HISTORICAL_ROOT
    return state.block_roots[slot % SLOTS_PER_HISTORICAL_ROOT]

def get_randao_mix(state: BeaconState, epoch: Epoch) -> Bytes32:
    """
    Return the randao mix at a recent ``epoch``.
    """
    return state.randao_mixes[epoch % EPOCHS_PER_HISTORICAL_VECTOR]

def get_active_validator_indices(state: BeaconState, epoch: Epoch) -> Sequence[ValidatorIndex]:
    """
    Return the sequence of active validator indices at ``epoch``.
    """
    return [ValidatorIndex(i) for i, v in enumerate(state.validators) if is_active_validator(v, epoch)]

def get_validator_churn_limit(state: BeaconState) -> uint64:
    """
    Return the validator churn limit for the current epoch.
    """
    active_validator_indices = get_active_validator_indices(state, get_current_epoch(state))
    return max(MIN_PER_EPOCH_CHURN_LIMIT, len(active_validator_indices) // CHURN_LIMIT_QUOTIENT)

def get_seed(state: BeaconState, epoch: Epoch, domain_type: DomainType) -> Bytes32:
    """
    Return the seed at ``epoch``.
    """
    mix = get_randao_mix(state, Epoch(epoch + EPOCHS_PER_HISTORICAL_VECTOR - MIN_SEED_LOOKAHEAD - 1))  # Avoid underflow
    return hash(domain_type + int_to_bytes(epoch, length=8) + mix)

def get_committee_count_at_slot(state: BeaconState, slot: Slot) -> uint64:
    """
    Return the number of committees at ``slot``.
    """
    epoch = compute_epoch_at_slot(slot)
    return max(1, min(
        MAX_COMMITTEES_PER_SLOT,
        len(get_active_validator_indices(state, epoch)) // SLOTS_PER_EPOCH // TARGET_COMMITTEE_SIZE,
    ))

def get_beacon_committee(state: BeaconState, slot: Slot, index: CommitteeIndex) -> Sequence[ValidatorIndex]:
    """
    Return the beacon committee at ``slot`` for ``index``.
    """
    epoch = compute_epoch_at_slot(slot)
    committees_per_slot = get_committee_count_at_slot(state, slot)
    return compute_committee(
        indices=get_active_validator_indices(state, epoch),
        seed=get_seed(state, epoch, DOMAIN_BEACON_ATTESTER),
        index=(slot % SLOTS_PER_EPOCH) * committees_per_slot + index,
        count=committees_per_slot * SLOTS_PER_EPOCH,
    )

def get_beacon_proposer_index(state: BeaconState) -> ValidatorIndex:
    """
    Return the beacon proposer index at the current slot.
    """
    epoch = get_current_epoch(state)
    seed = hash(get_seed(state, epoch, DOMAIN_BEACON_PROPOSER) + int_to_bytes(state.slot, length=8))
    indices = get_active_validator_indices(state, epoch)
    return compute_proposer_index(state, indices, seed)

def get_total_balance(state: BeaconState, indices: Set[ValidatorIndex]) -> Gwei:
    """
    Return the combined effective balance of the ``indices``. (1 Gwei minimum to avoid divisions by zero.)
    """
    return Gwei(max(1, sum([state.validators[index].effective_balance for index in indices])))

def get_total_active_balance(state: BeaconState) -> Gwei:
    """
    Return the combined effective balance of the active validators.
    """
    return get_total_balance(state, set(get_active_validator_indices(state, get_current_epoch(state))))

def get_domain(state: BeaconState, domain_type: DomainType, message_epoch: Epoch=None) -> Domain:
    """
    Return the signature domain (fork version concatenated with domain type) of a message.
    """
    epoch = get_current_epoch(state) if message_epoch is None else message_epoch
    fork_version = state.fork.previous_version if epoch < state.fork.epoch else state.fork.current_version
    return compute_domain(domain_type, fork_version)

def get_indexed_attestation(state: BeaconState, attestation: Attestation) -> IndexedAttestation:
    """
    Return the indexed attestation corresponding to ``attestation``.
    """
    attesting_indices = get_attesting_indices(state, attestation.data, attestation.aggregation_bits)

    return IndexedAttestation(
        attesting_indices=sorted(attesting_indices),
        data=attestation.data,
        signature=attestation.signature,
    )

def get_attesting_indices(state: BeaconState,
                          data: AttestationData,
                          bits: Bitlist[MAX_VALIDATORS_PER_COMMITTEE]) -> Set[ValidatorIndex]:
    """
    Return the set of attesting indices corresponding to ``data`` and ``bits``.
    """
    committee = get_beacon_committee(state, data.slot, data.index)
    return set(index for i, index in enumerate(committee) if bits[i])

def increase_balance(state: BeaconState, index: ValidatorIndex, delta: Gwei) -> None:
    """
    Increase the validator balance at index ``index`` by ``delta``.
    """
    state.balances[index] += delta

def decrease_balance(state: BeaconState, index: ValidatorIndex, delta: Gwei) -> None:
    """
    Decrease the validator balance at index ``index`` by ``delta``, with underflow protection.
    """
    state.balances[index] = 0 if delta > state.balances[index] else state.balances[index] - delta

def initiate_validator_exit(state: BeaconState, index: ValidatorIndex) -> None:
    """
    Initiate the exit of the validator with index ``index``.
    """
    # Return if validator already initiated exit
    validator = state.validators[index]
    if validator.exit_epoch != FAR_FUTURE_EPOCH:
        return

    # Compute exit queue epoch
    exit_epochs = [v.exit_epoch for v in state.validators if v.exit_epoch != FAR_FUTURE_EPOCH]
    exit_queue_epoch = max(exit_epochs + [compute_activation_exit_epoch(get_current_epoch(state))])
    exit_queue_churn = len([v for v in state.validators if v.exit_epoch == exit_queue_epoch])
    if exit_queue_churn >= get_validator_churn_limit(state):
        exit_queue_epoch += Epoch(1)

    # Set validator exit epoch and withdrawable epoch
    validator.exit_epoch = exit_queue_epoch
    validator.withdrawable_epoch = Epoch(validator.exit_epoch + MIN_VALIDATOR_WITHDRAWABILITY_DELAY)

def slash_validator(state: BeaconState,
                    slashed_index: ValidatorIndex,
                    whistleblower_index: ValidatorIndex=None) -> None:
    """
    Slash the validator with index ``slashed_index``.
    """
    epoch = get_current_epoch(state)
    initiate_validator_exit(state, slashed_index)
    validator = state.validators[slashed_index]
    validator.slashed = True
    validator.withdrawable_epoch = max(validator.withdrawable_epoch, Epoch(epoch + EPOCHS_PER_SLASHINGS_VECTOR))
    state.slashings[epoch % EPOCHS_PER_SLASHINGS_VECTOR] += validator.effective_balance
    decrease_balance(state, slashed_index, validator.effective_balance // MIN_SLASHING_PENALTY_QUOTIENT)

    # Apply proposer and whistleblower rewards
    proposer_index = get_beacon_proposer_index(state)
    if whistleblower_index is None:
        whistleblower_index = proposer_index
    whistleblower_reward = Gwei(validator.effective_balance // WHISTLEBLOWER_REWARD_QUOTIENT)
    proposer_reward = Gwei(whistleblower_reward // PROPOSER_REWARD_QUOTIENT)
    increase_balance(state, proposer_index, proposer_reward)
    increase_balance(state, whistleblower_index, whistleblower_reward - proposer_reward)

def initialize_beacon_state_from_eth1(eth1_block_hash: Bytes32,
                                      eth1_timestamp: uint64,
                                      deposits: Sequence[Deposit]) -> BeaconState:
    state = BeaconState(
        genesis_time=eth1_timestamp - eth1_timestamp % SECONDS_PER_DAY + 2 * SECONDS_PER_DAY,
        eth1_data=Eth1Data(block_hash=eth1_block_hash, deposit_count=len(deposits)),
        latest_block_header=BeaconBlockHeader(body_root=hash_tree_root(BeaconBlockBody())),
        randao_mixes=[eth1_block_hash] * EPOCHS_PER_HISTORICAL_VECTOR,  # Seed RANDAO with Eth1 entropy
    )

    # Process deposits
    leaves = list(map(lambda deposit: deposit.data, deposits))
    for index, deposit in enumerate(deposits):
        deposit_data_list = List[DepositData, 2**DEPOSIT_CONTRACT_TREE_DEPTH](*leaves[:index + 1])
        state.eth1_data.deposit_root = hash_tree_root(deposit_data_list)
        process_deposit(state, deposit)

    # Process activations
    for index, validator in enumerate(state.validators):
        balance = state.balances[index]
        validator.effective_balance = min(balance - balance % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE)
        if validator.effective_balance == MAX_EFFECTIVE_BALANCE:
            validator.activation_eligibility_epoch = GENESIS_EPOCH
            validator.activation_epoch = GENESIS_EPOCH

    return state

def is_valid_genesis_state(state: BeaconState) -> bool:
    if state.genesis_time < MIN_GENESIS_TIME:
        return False
    if len(get_active_validator_indices(state, GENESIS_EPOCH)) < MIN_GENESIS_ACTIVE_VALIDATOR_COUNT:
        return False
    return True

def state_transition(state: BeaconState, signed_block: SignedBeaconBlock, validate_result: bool=True) -> BeaconState:
    # Process slots (including those with no blocks) since block
    process_slots(state, signed_block.message.slot)
    # Verify signature
    if validate_result:
        assert verify_block_signature(state, signed_block)
    # Process block
    process_block(state, signed_block.message)
    if validate_result:
        assert signed_block.message.state_root == hash_tree_root(state)  # Validate state root
    # Return post-state
    return state

def verify_block_signature(state: BeaconState, signed_block: SignedBeaconBlock) -> bool:
    proposer = state.validators[get_beacon_proposer_index(state)]
    domain = get_domain(state, DOMAIN_BEACON_PROPOSER)
    return bls_verify(proposer.pubkey, hash_tree_root(signed_block.message), signed_block.signature, domain)

def process_slots(state: BeaconState, slot: Slot) -> None:
    assert state.slot <= slot
    while state.slot < slot:
        process_slot(state)
        # Process epoch on the start slot of the next epoch
        if (state.slot + 1) % SLOTS_PER_EPOCH == 0:
            process_epoch(state)
        state.slot += Slot(1)

def process_slot(state: BeaconState) -> None:
    # Cache state root
    previous_state_root = hash_tree_root(state)
    state.state_roots[state.slot % SLOTS_PER_HISTORICAL_ROOT] = previous_state_root
    # Cache latest block header state root
    if state.latest_block_header.state_root == Bytes32():
        state.latest_block_header.state_root = previous_state_root
    # Cache block root
    previous_block_root = hash_tree_root(state.latest_block_header)
    state.block_roots[state.slot % SLOTS_PER_HISTORICAL_ROOT] = previous_block_root

def process_epoch(state: BeaconState) -> None:
    print("START PROCESS EPOCH", get_current_epoch(state))
    process_justification_and_finalization(state)
    process_rewards_and_penalties(state)
    process_registry_updates(state)
    # @process_reveal_deadlines
    # @process_challenge_deadlines
    process_slashings(state)
    # @update_period_committee
    process_final_updates(state)
    # @after_process_final_updates
    print("END PROCESS EPOCH")

def get_matching_source_attestations(state: BeaconState, epoch: Epoch) -> Sequence[PendingAttestation]:
    assert epoch in (get_previous_epoch(state), get_current_epoch(state))
    return state.current_epoch_attestations if epoch == get_current_epoch(state) else state.previous_epoch_attestations

def get_matching_target_attestations(state: BeaconState, epoch: Epoch) -> Sequence[PendingAttestation]:
    return [
        a for a in get_matching_source_attestations(state, epoch)
        if a.data.target.root == get_block_root(state, epoch)
    ]

def get_matching_head_attestations(state: BeaconState, epoch: Epoch) -> Sequence[PendingAttestation]:
    return [
        a for a in get_matching_source_attestations(state, epoch)
        if a.data.beacon_block_root == get_block_root_at_slot(state, a.data.slot)
    ]

def get_unslashed_attesting_indices(state: BeaconState,
                                    attestations: Sequence[PendingAttestation]) -> Set[uint64]:
    output = set()  # type: Set[uint64]
    for a in attestations:
        output = output.union(get_attesting_indices(state, a.data, a.aggregation_bits))
    return set(filter(lambda index: not state.validators[index].slashed, output))

def get_attesting_balance(state: BeaconState, attestations: Sequence[PendingAttestation]) -> uint64:
    return get_total_balance(state, get_unslashed_attesting_indices(state, attestations))

def process_justification_and_finalization(state: BeaconState) -> None:
    if get_current_epoch(state) <= GENESIS_EPOCH + 1:
        print("not processing justification and finalization")
        return

    previous_epoch = get_previous_epoch(state)
    current_epoch = get_current_epoch(state)
    old_previous_justified_checkpoint = state.previous_justified_checkpoint
    old_current_justified_checkpoint = state.current_justified_checkpoint
    print("old_previous", state.previous_justified_checkpoint.epoch)
    print("old_current", state.current_justified_checkpoint.epoch)

    # Process justifications
    state.previous_justified_checkpoint = state.current_justified_checkpoint
    state.justification_bits[1:] = state.justification_bits[:-1]
    state.justification_bits[0] = 0b0
    matching_target_attestations = get_matching_target_attestations(state, previous_epoch)  # Previous epoch
    if get_attesting_balance(state, matching_target_attestations) * 3 >= get_total_active_balance(state) * 2:
        state.current_justified_checkpoint = Checkpoint(epoch=previous_epoch,
                                                        root=get_block_root(state, previous_epoch))
        print("new current justified checkpoint", state.current_justified_checkpoint.epoch)
        state.justification_bits[1] = 0b1
    matching_target_attestations = get_matching_target_attestations(state, current_epoch)  # Current epoch
    if get_attesting_balance(state, matching_target_attestations) * 3 >= get_total_active_balance(state) * 2:
        state.current_justified_checkpoint = Checkpoint(epoch=current_epoch,
                                                        root=get_block_root(state, current_epoch))
        print("new current justified checkpoint", state.current_justified_checkpoint.epoch)
        state.justification_bits[0] = 0b1

    print("justification bits", state.justification_bits)
    # Process finalizations
    bits = state.justification_bits
    # The 2nd/3rd/4th most recent epochs are justified, the 2nd using the 4th as source
    if all(bits[1:4]) and old_previous_justified_checkpoint.epoch + 3 == current_epoch:
        state.finalized_checkpoint = old_previous_justified_checkpoint
    # The 2nd/3rd most recent epochs are justified, the 2nd using the 3rd as source
    if all(bits[1:3]) and old_previous_justified_checkpoint.epoch + 2 == current_epoch:
        state.finalized_checkpoint = old_previous_justified_checkpoint
    # The 1st/2nd/3rd most recent epochs are justified, the 1st using the 3rd as source
    if all(bits[0:3]) and old_current_justified_checkpoint.epoch + 2 == current_epoch:
        state.finalized_checkpoint = old_current_justified_checkpoint
    # The 1st/2nd most recent epochs are justified, the 1st using the 2nd as source
    if all(bits[0:2]) and old_current_justified_checkpoint.epoch + 1 == current_epoch:
        state.finalized_checkpoint = old_current_justified_checkpoint
    print("finalised checkpoint", state.finalized_checkpoint.epoch)

def get_base_reward(state: BeaconState, index: ValidatorIndex) -> Gwei:
    total_balance = get_total_active_balance(state)
    effective_balance = state.validators[index].effective_balance
    return Gwei(effective_balance * BASE_REWARD_FACTOR // integer_squareroot(total_balance) // BASE_REWARDS_PER_EPOCH)

def get_attestation_deltas(state: BeaconState) -> Tuple[Sequence[Gwei], Sequence[Gwei]]:
    previous_epoch = get_previous_epoch(state)
    total_balance = get_total_active_balance(state)
    rewards = [Gwei(0) for _ in range(len(state.validators))]
    penalties = [Gwei(0) for _ in range(len(state.validators))]
    eligible_validator_indices = [
        ValidatorIndex(index) for index, v in enumerate(state.validators)
        if is_active_validator(v, previous_epoch) or (v.slashed and previous_epoch + 1 < v.withdrawable_epoch)
    ]

    # Micro-incentives for matching FFG source, FFG target, and head
    matching_source_attestations = get_matching_source_attestations(state, previous_epoch)
    matching_target_attestations = get_matching_target_attestations(state, previous_epoch)
    matching_head_attestations = get_matching_head_attestations(state, previous_epoch)
    for attestations in (matching_source_attestations, matching_target_attestations, matching_head_attestations):
        unslashed_attesting_indices = get_unslashed_attesting_indices(state, attestations)
        attesting_balance = get_total_balance(state, unslashed_attesting_indices)
        for index in eligible_validator_indices:
            if index in unslashed_attesting_indices:
                rewards[index] += get_base_reward(state, index) * attesting_balance // total_balance
            else:
                penalties[index] += get_base_reward(state, index)

    # Proposer and inclusion delay micro-rewards
    for index in get_unslashed_attesting_indices(state, matching_source_attestations):
        attestation = min([
            a for a in matching_source_attestations
            if index in get_attesting_indices(state, a.data, a.aggregation_bits)
        ], key=lambda a: a.inclusion_delay)
        proposer_reward = Gwei(get_base_reward(state, index) // PROPOSER_REWARD_QUOTIENT)
        rewards[attestation.proposer_index] += proposer_reward
        max_attester_reward = get_base_reward(state, index) - proposer_reward
        rewards[index] += Gwei(
            max_attester_reward // attestation.inclusion_delay
        )

    # Inactivity penalty
    finality_delay = previous_epoch - state.finalized_checkpoint.epoch
    if finality_delay > MIN_EPOCHS_TO_INACTIVITY_PENALTY:
        matching_target_attesting_indices = get_unslashed_attesting_indices(state, matching_target_attestations)
        for index in eligible_validator_indices:
            penalties[index] += Gwei(BASE_REWARDS_PER_EPOCH * get_base_reward(state, index))
            if index not in matching_target_attesting_indices:
                penalties[index] += Gwei(
                    state.validators[index].effective_balance * finality_delay // INACTIVITY_PENALTY_QUOTIENT
                )

    return rewards, penalties

def process_rewards_and_penalties(state: BeaconState) -> None:
    if get_current_epoch(state) == GENESIS_EPOCH:
        return

    rewards, penalties = get_attestation_deltas(state)
    for index in range(len(state.validators)):
        increase_balance(state, ValidatorIndex(index), rewards[index])
        decrease_balance(state, ValidatorIndex(index), penalties[index])

def process_registry_updates(state: BeaconState) -> None:
    # Process activation eligibility and ejections
    for index, validator in enumerate(state.validators):
        if (
            validator.activation_eligibility_epoch == FAR_FUTURE_EPOCH
            and validator.effective_balance == MAX_EFFECTIVE_BALANCE
        ):
            validator.activation_eligibility_epoch = get_current_epoch(state)

        if is_active_validator(validator, get_current_epoch(state)) and validator.effective_balance <= EJECTION_BALANCE:
            initiate_validator_exit(state, uint64(index))

    # Queue validators eligible for activation and not dequeued for activation prior to finalized epoch
    activation_queue = sorted([
        index for index, validator in enumerate(state.validators)
        if validator.activation_eligibility_epoch != FAR_FUTURE_EPOCH
        and validator.activation_epoch >= compute_activation_exit_epoch(state.finalized_checkpoint.epoch)
    ], key=lambda index: state.validators[index].activation_eligibility_epoch)
    # Dequeued validators for activation up to churn limit (without resetting activation epoch)
    for index in activation_queue[:get_validator_churn_limit(state)]:
        validator = state.validators[index]
        if validator.activation_epoch == FAR_FUTURE_EPOCH:
            validator.activation_epoch = compute_activation_exit_epoch(get_current_epoch(state))

def process_slashings(state: BeaconState) -> None:
    epoch = get_current_epoch(state)
    total_balance = get_total_active_balance(state)
    for index, validator in enumerate(state.validators):
        if validator.slashed and epoch + EPOCHS_PER_SLASHINGS_VECTOR // 2 == validator.withdrawable_epoch:
            increment = EFFECTIVE_BALANCE_INCREMENT  # Factored out from penalty numerator to avoid uint64 overflow
            penalty_numerator = validator.effective_balance // increment * min(sum(state.slashings) * 3, total_balance)
            penalty = penalty_numerator // total_balance * increment
            decrease_balance(state, ValidatorIndex(index), penalty)

def process_final_updates(state: BeaconState) -> None:
    current_epoch = get_current_epoch(state)
    next_epoch = Epoch(current_epoch + 1)
    # Reset eth1 data votes
    if (state.slot + 1) % SLOTS_PER_ETH1_VOTING_PERIOD == 0:
        state.eth1_data_votes = []
    # Update effective balances with hysteresis
    for index, validator in enumerate(state.validators):
        balance = state.balances[index]
        HALF_INCREMENT = EFFECTIVE_BALANCE_INCREMENT // 2
        if balance < validator.effective_balance or validator.effective_balance + 3 * HALF_INCREMENT < balance:
            validator.effective_balance = min(balance - balance % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE)
    # Reset slashings
    state.slashings[next_epoch % EPOCHS_PER_SLASHINGS_VECTOR] = Gwei(0)
    # Set randao mix
    state.randao_mixes[next_epoch % EPOCHS_PER_HISTORICAL_VECTOR] = get_randao_mix(state, current_epoch)
    # Set historical root accumulator
    if next_epoch % (SLOTS_PER_HISTORICAL_ROOT // SLOTS_PER_EPOCH) == 0:
        historical_batch = HistoricalBatch(block_roots=state.block_roots, state_roots=state.state_roots)
        state.historical_roots.append(hash_tree_root(historical_batch))
    # Rotate current/previous epoch attestations
    state.previous_epoch_attestations = state.current_epoch_attestations
    state.current_epoch_attestations = []

def process_block(state: BeaconState, block: BeaconBlock) -> None:
    process_block_header(state, block)
    process_randao(state, block.body)
    process_eth1_data(state, block.body)
    process_operations(state, block.body)

def process_block_header(state: BeaconState, block: BeaconBlock) -> None:
    # Verify that the slots match
    assert block.slot == state.slot
    # Verify that the parent matches
    assert block.parent_root == hash_tree_root(state.latest_block_header)
    # Save current block as the new latest block
    state.latest_block_header = BeaconBlockHeader(
        slot=block.slot,
        parent_root=block.parent_root,
        # `state_root` is zeroed and overwritten in the next `process_slot` call
        body_root=hash_tree_root(block.body),
    )
    # Verify proposer is not slashed
    proposer = state.validators[get_beacon_proposer_index(state)]
    assert not proposer.slashed

def process_randao(state: BeaconState, body: BeaconBlockBody) -> None:
    epoch = get_current_epoch(state)
    # Verify RANDAO reveal
    proposer = state.validators[get_beacon_proposer_index(state)]
    assert bls_verify(proposer.pubkey, hash_tree_root(epoch), body.randao_reveal, get_domain(state, DOMAIN_RANDAO))
    # Mix in RANDAO reveal
    mix = xor(get_randao_mix(state, epoch), hash(body.randao_reveal))
    state.randao_mixes[epoch % EPOCHS_PER_HISTORICAL_VECTOR] = mix

def process_eth1_data(state: BeaconState, body: BeaconBlockBody) -> None:
    state.eth1_data_votes.append(body.eth1_data)
    if state.eth1_data_votes.count(body.eth1_data) * 2 > SLOTS_PER_ETH1_VOTING_PERIOD:
        state.eth1_data = body.eth1_data

def process_operations(state: BeaconState, body: BeaconBlockBody) -> None:
    # Verify that outstanding deposits are processed up to the maximum number of deposits
    assert len(body.deposits) == min(MAX_DEPOSITS, state.eth1_data.deposit_count - state.eth1_deposit_index)

    for operations, function in (
        (body.proposer_slashings, process_proposer_slashing),
        (body.attester_slashings, process_attester_slashing),
        (body.attestations, process_attestation),
        (body.deposits, process_deposit),
        (body.voluntary_exits, process_voluntary_exit),
        # @process_shard_receipt_proofs
    ):
        for operation in operations:
            function(state, operation)

def process_proposer_slashing(state: BeaconState, proposer_slashing: ProposerSlashing) -> None:
    proposer = state.validators[proposer_slashing.proposer_index]
    # Verify slots match
    assert proposer_slashing.header_1.slot == proposer_slashing.header_2.slot
    # But the headers are different
    assert proposer_slashing.header_1 != proposer_slashing.header_2
    # Check proposer is slashable
    assert is_slashable_validator(proposer, get_current_epoch(state))
    # Signatures are valid
    for header in (proposer_slashing.header_1, proposer_slashing.header_2):
        domain = get_domain(state, DOMAIN_BEACON_PROPOSER, compute_epoch_at_slot(header.slot))
        assert bls_verify(proposer.pubkey, signing_root(header), header.signature, domain)

    slash_validator(state, proposer_slashing.proposer_index)

def process_attester_slashing(state: BeaconState, attester_slashing: AttesterSlashing) -> None:
    attestation_1 = attester_slashing.attestation_1
    attestation_2 = attester_slashing.attestation_2
    assert is_slashable_attestation_data(attestation_1.data, attestation_2.data)
    assert is_valid_indexed_attestation(state, attestation_1)
    assert is_valid_indexed_attestation(state, attestation_2)

    slashed_any = False
    indices = set(attestation_1.attesting_indices).intersection(attestation_2.attesting_indices)
    for index in sorted(indices):
        if is_slashable_validator(state.validators[index], get_current_epoch(state)):
            slash_validator(state, index)
            slashed_any = True
    assert slashed_any

def process_attestation(state: BeaconState, attestation: Attestation) -> None:
    data = attestation.data
    assert data.index < get_committee_count_at_slot(state, data.slot)
    assert data.target.epoch in (get_previous_epoch(state), get_current_epoch(state))
    assert data.slot + MIN_ATTESTATION_INCLUSION_DELAY <= state.slot <= data.slot + SLOTS_PER_EPOCH

    committee = get_beacon_committee(state, data.slot, data.index)
    assert len(attestation.aggregation_bits) == len(committee)

    pending_attestation = PendingAttestation(
        data=data,
        aggregation_bits=attestation.aggregation_bits,
        inclusion_delay=state.slot - data.slot,
        proposer_index=get_beacon_proposer_index(state),
    )

    if data.target.epoch == get_current_epoch(state):
        assert data.source == state.current_justified_checkpoint
        state.current_epoch_attestations.append(pending_attestation)
    else:
        assert data.source == state.previous_justified_checkpoint
        state.previous_epoch_attestations.append(pending_attestation)

    # Check signature
    assert is_valid_indexed_attestation(state, get_indexed_attestation(state, attestation))

def process_deposit(state: BeaconState, deposit: Deposit) -> None:
    # Verify the Merkle branch
    assert is_valid_merkle_branch(
        leaf=hash_tree_root(deposit.data),
        branch=deposit.proof,
        depth=DEPOSIT_CONTRACT_TREE_DEPTH + 1,  # Add 1 for the `List` length mix-in
        index=state.eth1_deposit_index,
        root=state.eth1_data.deposit_root,
    )

    # Deposits must be processed in order
    state.eth1_deposit_index += 1

    pubkey = deposit.data.pubkey
    amount = deposit.data.amount
    validator_pubkeys = [v.pubkey for v in state.validators]
    if pubkey not in validator_pubkeys:
        # Verify the deposit signature (proof of possession) for new validators.
        # Note: The deposit contract does not check signatures.
        # Note: Deposits are valid across forks, thus the deposit domain is retrieved directly from `compute_domain`.
        domain = compute_domain(DOMAIN_DEPOSIT)
        deposit_message = DepositMessage(
            pubkey=deposit.data.pubkey,
            withdrawal_credentials=deposit.data.withdrawal_credentials,
            amount=deposit.data.amount)
        if not bls_verify(pubkey, hash_tree_root(deposit_message), deposit.data.signature, domain):
            return

        # Add validator and balance entries
        state.validators.append(Validator(
            pubkey=pubkey,
            withdrawal_credentials=deposit.data.withdrawal_credentials,
            activation_eligibility_epoch=FAR_FUTURE_EPOCH,
            activation_epoch=FAR_FUTURE_EPOCH,
            exit_epoch=FAR_FUTURE_EPOCH,
            withdrawable_epoch=FAR_FUTURE_EPOCH,
            effective_balance=min(amount - amount % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE),
        ))
        state.balances.append(amount)
    else:
        # Increase balance by deposit amount
        index = ValidatorIndex(validator_pubkeys.index(pubkey))
        increase_balance(state, index, amount)

def process_voluntary_exit(state: BeaconState, signed_voluntary_exit: SignedVoluntaryExit) -> None:
    voluntary_exit = signed_voluntary_exit.message
    validator = state.validators[voluntary_exit.validator_index]
    # Verify the validator is active
    assert is_active_validator(validator, get_current_epoch(state))
    # Verify the validator has not yet exited
    assert validator.exit_epoch == FAR_FUTURE_EPOCH
    # Exits must specify an epoch when they become valid; they are not valid before then
    assert get_current_epoch(state) >= voluntary_exit.epoch
    # Verify the validator has been active long enough
    assert get_current_epoch(state) >= validator.activation_epoch + PERSISTENT_COMMITTEE_PERIOD
    # Verify signature
    domain = get_domain(state, DOMAIN_VOLUNTARY_EXIT, voluntary_exit.epoch)
    assert bls_verify(validator.pubkey, hash_tree_root(voluntary_exit), signed_voluntary_exit.signature, domain)
    # Initiate exit
    initiate_validator_exit(state, voluntary_exit.validator_index)

#####

def get_committee_assignment(state: BeaconState,
                             epoch: uint64,
                             validator_index: uint64
                             ) -> Optional[Tuple[Sequence[uint64], uint64, uint64]]:
    """
    Return the committee assignment in the ``epoch`` for ``validator_index``.
    ``assignment`` returned is a tuple of the following form:
        * ``assignment[0]`` is the list of validators in the committee
        * ``assignment[1]`` is the index to which the committee is assigned
        * ``assignment[2]`` is the slot at which the committee is assigned
    Return None if no assignment.
    """
    next_epoch = get_current_epoch(state) + 1
    assert epoch <= next_epoch

    start_slot = compute_start_slot_at_epoch(epoch)
    for slot in range(start_slot, start_slot + SLOTS_PER_EPOCH):
        for index in range(get_committee_count_at_slot(state, slot)):
            committee = get_beacon_committee(state, slot, index)
            if validator_index in committee:
                return committee, index, slot
    return None
