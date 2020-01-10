import matplotlib.pyplot as plt

from constants import *
from eth2 import *
from perfect_world import perfect_reward

class Validator:
    def __init__(self):
        self.state_balance = MAX_EFFECTIVE_BALANCE
        self.effective_balance = MAX_EFFECTIVE_BALANCE

    def increase_balance(self, delta):
        self.state_balance += delta

    def decrease_balance(self, delta):
        self.state_balance = 0 if delta > self.state_balance else self.state_balance - delta

    def update_effective_balance(self):
        HALF_INCREMENT = EFFECTIVE_BALANCE_INCREMENT // 2
        if self.state_balance < self.effective_balance or self.effective_balance + 3 * HALF_INCREMENT < self.state_balance:
            self.effective_balance = quantised_update_function(self.state_balance)

def get_total_stake(validators):
    return sum([v.effective_balance for v in validators])

alpha = 0.4
validators = [Validator() for i in range(100)]
cutoff = int(alpha * len(validators))
last_finalized_epoch = -1
horizon = 10000
penalties_offline = [0 for i in range(horizon)]
effective_balances_offline = [0 for i in range(horizon)]
state_balances_offline = [0 for i in range(horizon)]

for e in range(horizon):
    if e % 1000 == 0: print "epoch", e
    offline_validator = validators[0]
    online_validator = validators[cutoff + 1]
    total_stake = get_total_stake(validators)
    finality_delay = e - last_finalized_epoch

    reward_online = perfect_reward(online_validator.effective_balance, total_stake)
    penalty_online = 0
    reward_offline = 0
    penalty_offline = get_base_reward(offline_validator.effective_balance, total_stake)

    if finality_delay > MIN_EPOCHS_TO_INACTIVITY_PENALTY:
        penalty_online += BASE_REWARDS_PER_EPOCH * get_base_reward(online_validator.effective_balance, total_stake)
        penalty_offline += BASE_REWARDS_PER_EPOCH * get_base_reward(offline_validator.effective_balance, total_stake)
        penalty_offline += offline_validator.effective_balance * finality_delay // INACTIVITY_PENALTY_QUOTIENT

    penalties_offline[e] = penalty_offline
    effective_balances_offline[e] = validators[0].effective_balance
    state_balances_offline[e] = validators[0].state_balance

    # print reward_offline
    # print reward_online

    for i, v in enumerate(validators):
        if i <= cutoff: # offline validator
            v.increase_balance(reward_offline)
            v.decrease_balance(penalty_offline)
        else:
            v.increase_balance(reward_online)
            v.decrease_balance(penalty_online)
        v.update_effective_balance()

    stake_offline = sum([v.effective_balance for v in validators[:(cutoff+1)]])
    stake_online = sum([v.effective_balance for v in validators[(cutoff+1):]])

    if e % 1000 == 0:
        print "Offline validator balances", (validators[0].state_balance, validators[0].effective_balance)
        print "Online validator balances", (validators[cutoff+1].state_balance, validators[cutoff+1].effective_balance)
        print "stake online", stake_online
        print "Fraction of stake online", float(stake_online) / float(total_stake)

plt.plot(range(horizon), penalties_offline)
plt.show()
plt.plot(range(horizon), effective_balances_offline)
plt.show()
plt.plot(range(horizon), state_balances_offline)
plt.show()
