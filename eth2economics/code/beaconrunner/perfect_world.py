from constants import *
from eth2 import get_base_reward

epochs_per_year = SECONDS_PER_DAY / SECONDS_PER_SLOT * 365 / SLOTS_PER_EPOCH

def perfect_reward(effective_balance, total_stake):
    br = get_base_reward(effective_balance, total_stake)
    r1 = 3 * br
    r2 = br - br // PROPOSER_REWARD_QUOTIENT
    r3 = br // (PROPOSER_REWARD_QUOTIENT * SLOTS_PER_EPOCH * MAX_COMMITTEES_PER_SLOT) # returns 0... investigate
    return r1 + r2 + r3
