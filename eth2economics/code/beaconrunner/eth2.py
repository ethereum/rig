from constants import EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE, BASE_REWARD_FACTOR, BASE_REWARDS_PER_EPOCH
from specs import integer_squareroot

###
### Functions pulled from specs with minimal adaptation
###

def quantised_update(balance):
    return min(balance - balance % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE)

def get_base_reward(effective_balance, total_balance):
    return effective_balance * BASE_REWARD_FACTOR // integer_squareroot(total_balance) // BASE_REWARDS_PER_EPOCH

def eth_to_gwei(eth):
    return eth * (10 ** 9)