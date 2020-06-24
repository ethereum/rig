# EIP 1559 implementers' call #3 notes

## 1559 and the escalator

If it is decided to combine 1559 and the escalator, I believe the [floating escalator](combination.md) is the best way to do so. It is the only option for which it is possible to unbundle the 1559 side and the escalator side, allowing us to implement 1559 first and decide later on (or in concert) whether the escalator rule should be proposed.

As a reminder, the escalator rule governs the premium:

- `p[t] = startpremium + (t - startblock) / (endblock - startblock) * (maxpremium - startpremium)`

In the floating escalator, we simply add the escalating premium to the current basefee `b[t]`.

```python
gasprice[t] = min(
  b[t] + p[t],
  maxfee
)

# Include only if
assert gasprice[t] >= b[t]
```

A user must decide `maxfee`, `startpremium`, `maxpremium`, `startblock` and `endblock`.

In addition, it is possible even with the escalator rule to emulate the behaviour of a 1559 tx with parameters `gas_premium` and `maxfee`, by setting `startblock` to the current block, `endblock` to an outrageously far away block and `startpremium == maxpremium == gas_premium`. This should help for compatibility and UX if and once the escalator rule is adopted to move the premium value.

## 2718 and 1559

I don't have much to say about this. It seems 2718 offers a clean way to upgrade transaction patterns. This is perhaps helpful with the above?

## (In progress) Simulations

We have the beginning of a more robust environment for agent-based simulations [here](abm1559.ipynb). We need to think through how agents should behave but initial tests show basefee converges quickly when the demand is at steady-state (e.g., same expectation of arrivals between two blocks). There is also support for escalator-style transactions but untested so far.

Currently, agents can have two different cost functions, one where they incur a cost for waiting one extra block that is fixed, with some value for having their transaction included and one where this value is discounted over time (the later inclusion, the smaller the value). Agents decide to enter or not based on their estimation of profit: if they expect to realise a negative profit, they balk and do not submit their transaction.

Note that _without the option to cancel their transaction (for free or at some predictible cost)_, an agent may realise a negative profit after all if their estimation was too optimistic. This violates ex post individual rationality.

The current agent estimation of waiting time is pretty dumb (they simply expect to wait 5 blocks). A better estimator must depend on the submitted transaction parameters (the higher the premium/maxfee, the lower their expected waiting time) and could look like the estimators currently used by wallets. This will also be helpful to test these estimators empirically and decide on good transaction default values.

## (Important) Wallet defaults

How should wallets set `max_fee` and `gas_premium`? We look for good default values to proposer to users. In the current UX paradigm, users are presented with 4 options:

- Three of them suggest values corresponding to "fast", "average" and "slow" inclusions.
- Otherwise, users can set their own transaction values.

Suppose a wallet offers defaults pegged to the basefee, e.g., three defaults $\rho_1 < \rho_2 < \rho_3$ such that proposed maxfees are $m_i = (1+\rho_i) b(t)$. Assuming users broadly follow wallet defaults (they seem to), miners now make a higher profit when basefee is higher, all else equal.

It was suggested to default to a fixed premium for users, e.g., 1 Gwei, or the amount of Gwei that would exactly compensate a miner for the extra ommer risk of including the transaction in their block. The tip however will likely decide the speed of inclusion of the transaction, given that the tip is received by miners. We prefer high value or time-sensitive transactions to get in first and with a fixed premium, may not be able to discriminate between low and high value instances.

### Pegged premium rule: A naive proposal that doesn't work

A default that respects this intuition is pegging the premium to the proposed maxfee. We assume then that users only declare their maxfee and the premium is set in protocol, taking e.g. one hundredth of the declared maxfee.

I value my transaction a lot and am ready to pay 10 Gwei for it. The default sets my premium to 10 / 100 = 0.1 Gwei. Someone else who values theirs less, e.g., is only ready to pay up to 5 Gwei for it, has their premium set to 5 / 100 = 0.05 Gwei. Miners prefer my transaction to theirs. This also collapses the number of parameters to set from 2 to 1.

When the premium is equal to a fixed fraction of the maxfee, the tip becomes a consistent transaction order, in addition to representing exactly the miner profit. Whenever $m_i < m_j$, two maxfees of two users $i$ and $j$, we _always_ have $p_i < p_j$ (premiums) and $t_i < t_j$ (tips).

From an incentive-compatibility point of view, a user who wants to "game" the system by inflating their maxfee to inflate their tip exposes themselves to a high transaction fee, in the case where basefee increases before they are included.

But there is a trivial strategy to defeat this rule: a user could declare a maxfee they would not be ready to pay and monitor the basefee, cancelling their transaction whenever basefee rises above their true (undeclared) maxfee. So the pegged premium rule is not incentive compatible.

## (Important) Client strategies

We need to figure out how clients handle pending transactions. In the current paradigm, clients can simply rank and update their list of pending transactions based on the gasprice. This is *not true* when users can set both the maxfee and the premium! For instance, when basefee is equal to 5, consider these two users:

| Basefee = 5 | Maxfee | Premium | Tip |
|-|-|-|-|
| **User A** | 10 | 8 | 5 |
| **User B** | 15 | 6 | 6 |

We like ranking by premiums since these do not vary over time. It means miners can easily update their pending transactions list. But ranking by premiums, a miner would prefer user A to user B, even though the miner would receive a greater payoff from including B.

So we must rank by tips, in which case B is preferred. But tips are time-varying! Suppose basefee now drops to 2.

| Basefee = 2 | Maxfee | Premium | Tip |
|-|-|-|-|
| **User A** | 10 | 8 | 8 |
| **User B** | 15 | 6 | 6 |

Now user A is preferred to B. Miners must re-rank all pending transactions between each block based on the new basefee.

This issue compounds with time-varying premiums, as suggested in the [floating escalator](combination.md) for instance.

Clients must also handle their memory -- by default I believe, clients only keep around the current 8092 most profitable transactions in their transaction pools. Should a client keep around a currently invalid transaction (one where current basefee is higher than maxfee) in the hope that when basefee lowers they will reap a good tip?

When basefee is high, some high-premium transactions may be submerged.

| Basefee = 10 | Maxfee | Premium | Tip |
|-|-|-|-|
| **User A** | 9 | 4 | - |
| **User B** | 15 | 3 | 3 |

But let the tide ebb, and the transaction is now preferred.

| Basefee = 5 | Maxfee | Premium | Tip |
|-|-|-|-|
| **User A** | 9 | 4 | 4 |
| **User B** | 15 | 3 | 3 |

With some work it is likely possible to find a good rule / heuristics to have a pretty good approximation of the optimum. This is something that we should discuss more with the Nethermind team too as they raised this concern in their 1559 document.

## (Nice to have) Equilibrium strategy

We can take a cue from [Huberman et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3025604) and analyse the transaction fee market as a strategic game of queueing. Assuming all transactions have constant gas requirements, how should we define the game?

- It is a batched service queue (a round of service includes a maximum of _K_ transactions). Normalise time units such that service happens deterministically each time step ($\mu = 1$).
- There is one server/miner (logically, although practically the server/miner varies between services).
- The server sets a _dynamic_ minimum fee (the basefee $b(t)$), observed by users before deciding whether to enter the queue or balk.
- The dynamic fee depends on the congestion.

We can use the model of users having some fixed value $v$ for the transaction, and random per-time-unit costs (distributed according to some CDF $F$). A user with per-time-unit cost $c$ served after $w$ time steps at time $t$ who submitted _tip_ $\overline{p}(t) = \min(maxfee - b(t), premium)$ has payoff $v - \overline{p}(t) - c \cdot w$. We look for equilibrium waiting times and strategies. Users come in following a Poisson arrival process of rate $\lambda$ (i.e., during $t$ time units, we expect $t\lambda$ arrivals).

This differs from the Huberman et al. case since we have a time-varying basefee and thus time-varying premiums. In the Huberman et al. setting, there exists an equilibrium distribution of bids $G$ such that a player bids $p$ and expects payoff $v - p - c \cdot w(p|G)$, where $w(p|G)$ denotes that the waiting time $w$ depends on $p$ given $G$. $G$ is entirely determined by $F$ and $\lambda$.

The equivalent of $G$ in EIP 1559 is the distribution over $\overline{p}$ which is what miners consider for inclusion. We look for the following properties:

- Users with greater costs always offer greater tips, i.e., whenever $c_i \leq c_j$ for two users $i$ and $j$, $\overline{p}_i(t) \leq \overline{p}_j(t)$ for all $t$. In the case where all users propose the same premium, this is true if players with greater costs choose higher $maxfee$.
- An equilibrium basefee $\overline{b}$ given $\lambda$ and $F$. Demand shocks are interpreted as increasing $\lambda$.
