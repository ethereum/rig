from ssz_typing import (uint64, Bytes4, Bytes8, Bytes32, Bytes48, Bytes96)

### Types
class Slot(uint64):
    pass

class Epoch(uint64):
    pass

class CommitteeIndex(uint64):
    pass

class ValidatorIndex(uint64):
    pass

class Gwei(uint64):
    pass

class Root(Bytes32):
    pass

class Version(Bytes4):
    pass

class DomainType(Bytes4):
    pass

class Domain(Bytes8):
    pass

class BLSPubkey(Bytes48):
    pass

class BLSSignature(Bytes96):
    pass

# defaults to emulate "zero types"
default_slot = Slot(0)
default_epoch = Epoch(0)
default_committee_index = CommitteeIndex(0)
default_validator_index = ValidatorIndex(0)
default_gwei = Gwei(0)
default_version = Version(b"\x00" * 4)