import time
from typing import Set, Optional, Sequence, Tuple, Dict, Text
from dataclasses import dataclass, field
import specs

from eth2spec.utils.ssz.ssz_impl import hash_tree_root
from eth2spec.utils.ssz.ssz_typing import Container, List, uint64, Bitlist, Bytes32

log = True
logged_val = 1

frequency = 1
assert frequency in [1, 10, 100, 1000] 

class ValidatorMove(object):
    time: uint64
    slot: specs.Slot
    move: str
        
    def __init__(self, time, slot, move):
        self.time = time
        self.slot = slot
        self.move = move
        
class ValidatorData:
    slot: specs.Slot
    time_ms: uint64
    head_root: specs.Root
    current_epoch: specs.Epoch
    current_attest_slot: specs.Slot
    current_committee_index: specs.CommitteeIndex
    current_committee: List[specs.ValidatorIndex, specs.MAX_VALIDATORS_PER_COMMITTEE]
    next_attest_slot: specs.Slot
    next_committee_index: specs.CommitteeIndex
    next_committee: List[specs.ValidatorIndex, specs.MAX_VALIDATORS_PER_COMMITTEE]
    last_slot_attested: Optional[specs.Slot]
    current_proposer_duties: Sequence[bool]
    last_slot_proposed: Optional[specs.Slot]
    recorded_attestations: Sequence[specs.Root]

class BRValidator:
    validator_index: specs.ValidatorIndex
    store: specs.Store
    history: List[ValidatorMove, specs.VALIDATOR_REGISTRY_LIMIT]
    data: ValidatorData

    def __init__(self, state, validator_index):
        self.validator_index = validator_index
        self.store = specs.get_forkchoice_store(state)
        self.history = []
        
        self.data = ValidatorData()
        self.data.time_ms = self.store.time * 1000
        self.data.recorded_attestations = []
        
        self.data.slot = specs.get_current_slot(self.store)
        self.data.current_epoch = specs.compute_epoch_at_slot(self.data.slot)
        
        self.data.head_root = specs.get_head(self.store)
        current_state = state.copy()
        specs.process_slots(current_state, self.data.slot)
        
        self.update_attester(current_state, self.data.current_epoch)
        self.update_proposer(current_state)
        self.update_data()
        
    def update_time(self) -> None:
        self.data.time_ms += 1000 / frequency
        if self.data.time_ms % 1000 == 0:
            specs.on_tick(self.store, self.store.time + 1)
            
            # If a new slot starts, we update
            if specs.get_current_slot(self.store) != self.data.slot:
                self.update_data(new_slot = True)
                
    def forward_by(self, seconds) -> None:
        number_ticks = seconds * frequency
        for i in range(number_ticks):
            self.update_time()
    
    def update_attester(self, current_state, epoch):
        if self.validator_index == logged_val and log: print(">>> recomputing attester")
        current_epoch = specs.get_current_epoch(current_state)
        # When is the validator scheduled to attest in `epoch`?
        (committee, committee_index, attest_slot) = specs.get_committee_assignment(
            current_state,
            epoch,
            self.validator_index)
        if epoch == current_epoch:
            self.data.current_attest_slot = attest_slot
            self.data.current_committee_index = committee_index
            self.data.current_committee = committee
        elif epoch == current_epoch + 1:
            self.data.next_attest_slot = attest_slot
            self.data.next_committee_index = committee_index
            self.data.next_committee = committee
    
    def update_proposer(self, current_state):
        if self.validator_index == logged_val and log: print(">>> recomputing proposer")
        current_epoch = specs.get_current_epoch(current_state)
        
        start_slot = specs.compute_start_slot_at_epoch(current_epoch)
        
        start_state = current_state.copy() if start_slot == current_state.slot else \
        self.store.block_states[specs.get_block_root(current_state, current_epoch)].copy()
                            
        current_proposer_duties = []
        for slot in range(start_slot, start_slot + specs.SLOTS_PER_EPOCH):
            if slot < start_state.slot:
                current_proposer_duties += [False]
                continue
            
            specs.process_slots(start_state, slot)
            current_proposer_duties += [specs.get_beacon_proposer_index(start_state) == self.validator_index]
                
        self.data.current_proposer_duties = current_proposer_duties
        
    def update_attest_move(self):
        # When was the last attestation?
        slots_attested = sorted([log.slot for log in self.history if log.move == "attest"], reverse = True)
        self.data.last_slot_attested = None if len(slots_attested) == 0 else slots_attested[0]
        
    def update_propose_move(self):
        # When was the last block proposal?
        slots_proposed = sorted([log.slot for log in self.history if log.move == "propose"], reverse = True)
        self.data.last_slot_proposed = None if len(slots_proposed) == 0 else slots_proposed[0]
    
    def update_data(self, new_slot = False) -> None:
        start = time.time()
        # The head may change if we recorded a new block/new attestation
        # Attester/proposer responsibilities may change if head changes *and*
        # canonical chain changes to further back from start current epoch
        #
        # ---x------
        #    \        x is fork point
        #     -----
        #
        # In the following attester = attester responsibilities for current epoch
        #                  proposer = proposer responsibilities for current epoch
        #
        # - If x after current epoch change (---|--x , | = start current epoch), proposer and attester don't change
        # - If x between start of previous epoch and start of current epoch (--||--x---|-- , || = start previous epoch)
        #   proposer changes but not attester
        # - If x before start of previous epoch (--x--||-----|----) both proposer and attester change
        if self.validator_index == logged_val and log: print("------ update_data")
        slot = specs.get_current_slot(self.store)
    
        # Current epoch in validator view
        current_epoch = specs.compute_epoch_at_slot(slot)

        self.update_attest_move()
        self.update_propose_move()
        if self.validator_index == logged_val and log: print("updated moves", time.time() - start)
        
        # Did the validator receive a block in this slot?
        received_block = len([block for block_root, block in self.store.blocks.items() if block.slot == slot]) > 0
        if self.validator_index == logged_val and log: print("updated received", time.time() - start)
        
        if not new_slot:
            # It's not a new slot, we are here because a new block/attestation was received
            
            # Getting the current state, fast-forwarding from the head
            head_root = specs.get_head(self.store)
            if self.validator_index == logged_val and log: print("got head", time.time() - start)

            if self.data.head_root != head_root:
                lca = lowest_common_ancestor(self.store, self.data.head_root, head_root, self.validator_index == logged_val and log)
                lca_epoch = specs.compute_epoch_at_slot(lca.slot)

                if lca_epoch == current_epoch:
                    # do nothing
                    pass
                else:
                    head_state = self.store.block_states[head_root]
                    current_state = head_state.copy()
                    specs.process_slots(current_state, slot)
                    if lca_epoch == current_epoch - 1:
                        self.update_proposer(current_state)
                    else:
                        self.update_proposer(current_state)
                        self.update_attester(current_state, current_epoch)
                self.data.head_root = head_root
                
        else:
            # It's a new slot. We should update our proposer/attester duties
            # if it's also a new epoch. If not we do nothing.
            if self.data.current_epoch == current_epoch:
                pass
            
            current_state = self.store.block_states[self.data.head_root].copy()
            specs.process_slots(current_state, slot)

            # We need to check our proposer role for this new epoch
            self.update_proposer(current_state)

            # We need to check our attester role for this new epoch
            self.update_attester(current_state, current_epoch)
            
            
        
        if self.validator_index == logged_val and log: print("updated proposers/attesters", time.time() - start)
            
        self.data.slot = slot
        self.data.current_epoch = current_epoch
        self.data.received_block = received_block
        if self.validator_index == logged_val and log: print("------ update_data", time.time() - start)
        
    def log_block(self, item: specs.SignedBeaconBlock) -> None:
        self.history.append(ValidatorMove(
            time = self.data.time_ms,
            slot = item.message.slot,
            move = "propose"
        ))

    def log_attestation(self, item: specs.Attestation) -> None:
        self.history.append(ValidatorMove(
            time = self.data.time_ms,
            slot = item.data.slot,
            move = "attest"
        ))

    def record_block(self, item: specs.SignedBeaconBlock) -> bool:
        # If we already know about the block, do nothing
        start = time.time()
#         if self.validator_index == logged_val and log: print("------ record_block")
        if hash_tree_root(item.message) in self.store.blocks:
#             if self.validator_index == logged_val and log: print("I already know block", time.time() - start)
            return False
                
        try:
            specs.on_block(self.store, item)
#             if self.validator_index == logged_val and log: print("Recorded block", time.time() - start)
        except:
#             if self.validator_index == logged_val and log: print("------ end record_block")
            return False
        
        for attestation in item.message.body.attestations:
#             if self.validator_index == logged_val and log: print("Recording attestation from block", time.time() - start)
            self.record_attestation(attestation)
        
#         if self.validator_index == logged_val and log: print("on_block done, atts recorded", time.time() - start, "\n------ end record_block")
        return True

    def record_attestation(self, item: specs.Attestation) -> bool:
        start = time.time()
#         if self.validator_index == logged_val and log: print("------ record_attestation")
        
        att_hash = hash_tree_root(item)
        
        # If we have already seen this attestation, no need to go further
        if att_hash in self.data.recorded_attestations:
#             if self.validator_index == logged_val and log: print("already know that att\n------ end record_attestation")
            return False
        
        try:
            specs.on_attestation(self.store, item)
            self.data.recorded_attestations += [att_hash]
#             if self.validator_index == logged_val and log: print("recorded att\n------ end record_attestation")
            return True
        except:
#             if self.validator_index == logged_val and log: print("error recording att\n------ end record_attestation")
            return False

    def check_backlog(self, known_items: Dict[str, Sequence[Container]]) -> None:
        start = time.time()
        if self.validator_index == logged_val and log: print("------- check_backlog")
        recorded_blocks = 0
        for block in known_items["blocks"]:
            recorded = self.record_block(block.item)
            if recorded:
                recorded_blocks += 1
        if self.validator_index == logged_val and log: print("finished recording blocks", time.time() - start)
        
        recorded_attestations = 0
        for attestation in known_items["attestations"]:
            recorded = self.record_attestation(attestation.item)
            if recorded:
                recorded_attestations += 1
        if self.validator_index == logged_val and log: print("finished recording attestations", time.time() - start)
        
        if recorded_blocks > 0 or recorded_attestations > 0:
            self.update_data()
        if self.validator_index == logged_val and log: print("done updating data", time.time() - start)
        
        if self.validator_index == logged_val and log: print("------- end check_backlog", time.time() - start)

            
def lowest_common_ancestor(store, old_head, new_head, log = False) -> Optional[specs.BeaconBlock]:
    # in most cases, old_head <- new_head
    # we sort of (loosely) optimise for this
    
    new_head_ancestors = [new_head]
    current_block = store.blocks[new_head]
    keep_searching = True
    while keep_searching:
        if log: print("keep searching")
        parent_root = current_block.parent_root
        parent_block = store.blocks[parent_root]
        if parent_root == old_head:
            if log: print("parent is old head")
            return store.blocks[old_head]
        elif parent_block.slot == 0 or \
        specs.compute_start_slot_at_epoch(store.finalized_checkpoint.epoch) > specs.compute_epoch_at_slot(parent_block.slot):
            keep_searching = False
        else:
            new_head_ancestors += [parent_root]
            current_block = parent_block
    
    # At this point, old_head wasn't an ancestor to new_head
    # We need to find old_head's ancestors
    current_block = store.blocks[old_head]
    keep_searching = True
    while keep_searching:
        parent_root = current_block.parent_root
        parent_block = store.blocks[parent_root]
        if parent_root in new_head_ancestors:
            return parent_block
        elif parent_root == Bytes32() or \
        specs.compute_start_slot_at_epoch(store.finalized_checkpoint.epoch) < specs.compute_epoch_at_slot(parent_block.slot):
            return None
    
            
### Attestation strategies            
            
def honest_attest(validator, known_items):
    # Unpacking
    validator_index = validator.validator_index
    store = validator.store
    committee_slot = validator.data.current_attest_slot
    committee_index = validator.data.current_committee_index
    committee = validator.data.current_committee
    
    # What am I attesting for?
    block_root = specs.get_head(store)
    head_state = store.block_states[block_root].copy()
    specs.process_slots(head_state, committee_slot)
    start_slot = specs.compute_start_slot_at_epoch(specs.get_current_epoch(head_state))
    epoch_boundary_block_root = block_root if start_slot == head_state.slot else specs.get_block_root_at_slot(head_state, start_slot)
    tgt_checkpoint = specs.Checkpoint(epoch=specs.get_current_epoch(head_state), root=epoch_boundary_block_root)
    
    att_data = specs.AttestationData(
        index = committee_index,
        slot = committee_slot,
        beacon_block_root = block_root,
        source = head_state.current_justified_checkpoint,
        target = tgt_checkpoint
    )

    # Set aggregation bits to myself only
    committee_size = len(committee)
    index_in_committee = committee.index(validator_index)
    aggregation_bits = Bitlist[specs.MAX_VALIDATORS_PER_COMMITTEE](*([0] * committee_size))
    aggregation_bits[index_in_committee] = True # set the aggregation bit of the validator to True
    attestation = specs.Attestation(
        aggregation_bits=aggregation_bits,
        data=att_data
    )
    
    if log: print("attestation", hash_tree_root(attestation), "for slot", committee_slot, "by validator", validator.validator_index, "source", store.justified_checkpoint.epoch, "and target", tgt_checkpoint.epoch)

    return attestation

### Aggregation helpers

def build_aggregate(attestations):
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

def aggregate_attestations(attestations):
    # Take in a set of attestations
    # Output aggregated attestations
    hashes = set([hash_tree_root(att.data) for att in attestations])
    return [build_aggregate(
        [att for att in attestations if att_hash == hash_tree_root(att.data)]
    ) for att_hash in hashes]

### Proposal strategies

def honest_propose(validator, known_items):
    slot = validator.data.slot
    head = validator.data.head_root
    
    attestations = known_items["attestations"]
    attestations = aggregate_attestations([att.item for att in attestations if slot <= att.item.data.slot + specs.SLOTS_PER_EPOCH])
    
    beacon_block_body = specs.BeaconBlockBody(
        attestations=attestations
    )

    beacon_block = specs.BeaconBlock(
        slot=slot,
        parent_root=head,
        body=beacon_block_body,
        proposer_index = validator.validator_index
    )
    
    state_root = specs.compute_new_state_root(validator.store.block_states[head].copy(), beacon_block)
    beacon_block.state_root = state_root
    
    signed_beacon_block = specs.SignedBeaconBlock(message=beacon_block)

    if log: print("honest validator", validator.validator_index, "propose a block for slot", slot)
    if log: print("block contains", len(signed_beacon_block.message.body.attestations), "attestations")
    return signed_beacon_block