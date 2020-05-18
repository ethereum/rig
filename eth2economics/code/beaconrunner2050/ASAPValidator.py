from typing import Optional

import specs
import validatorlib as vlib

class ASAPValidator(vlib.BRValidator):
    # Always $lash and prosper!
    
    def attest(self, known_items) -> Optional[specs.Attestation]: 
        # Not the moment to attest
        if self.data.current_attest_slot != self.data.slot:
            return None
        
        # Too early in the slot
        if (self.store.time - self.store.genesis_time) % specs.SECONDS_PER_SLOT < 4:
            return None
        
        # Already attested for this slot
        if self.data.last_slot_attested == self.data.slot:
            return None
            
        # honest attest
        return vlib.honest_attest(self, known_items)
    
    def propose(self, known_items) -> Optional[specs.SignedBeaconBlock]:
        # Not supposed to propose for current slot
        if not self.data.current_proposer_duties[self.data.slot % specs.SLOTS_PER_EPOCH]:
            return None
        
        # Already proposed for this slot
        if self.data.last_slot_proposed == self.data.slot:
            return None
        
        # honest propose
        return vlib.honest_propose(self, known_items)