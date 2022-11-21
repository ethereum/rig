# Combination EIP1559 / escalator

**TL;DR:** We present three models for combining EIP1559 and escalator. Of the three, only one really makes sense for us (the _floating escalator_ model), while the other two (_thresholded escalator_ and _fixed escalator_) are presented for the sake of providing a complete exploration of the design space.

## Base dynamics and parameters

### Base parameters

- `c` = target gas used
- `1 / d` = max rate of change
- `g[t]` = gas used by block t
- `b[t]` = basefee at block t
- `p[t]` = premium at block t

### Dynamics

**EIP 1559 dynamics**

- `b[t+1] = b[t] * (1 + (g[t] - c) / c / d)`

**Linear escalator, given `startblock`, `endblock`, `startpremium` and `maxpremium`**

- `p[t] = startpremium + (t - startblock) / (endblock - startblock) * (maxpremium - startpremium)`

## Thresholded escalator

**Intuition:** Vanilla escalator with the condition that a bid cannot be included if the `gasprice` is lower than the current `basefee`.

### User-specified parameters

- `startbid`
- `startblock`
- `endblock`
- `maxpremium`

### Computed parameters

- `startpremium = 0`

### Gas price

```python
gasprice[t] = startbid + p[t]

# Include only if
assert gasprice[t] >= b[t]
```

### Pros/cons

#### Pros

- "Pure" escalator, only modulated by the presence of the basefee which determines inclusion or not.
- Wallets can default to `startbid = b[t]`. This is the _fixed escalator_ model.

#### Cons

- Cannot write EIP 1559 simple strategy basefee + fixed premium under that model.

## Fixed escalator

**Intuition:** Vanilla escalator with a reasonable `startbid` parameter provided by the current `basefee`.

### User-specified parameters

- `startblock`
- `endblock`
- `maxfee`
- `startpremium`

### Computed parameters

- `maxpremium = maxfee - b[startblock]`

### Gas price

```python
gasprice[t] = min(
  max(b[startblock] + p[t], b[t]),
  b[startblock] + maxpremium
)

# Include only if
assert gasprice[t] >= b[t]
```

- Gas price set to either current basefee `b[t]` OR basefee at the start of the escalator `b[startblock]` + current premium `p[t]`, whichever is higher, bounded above by the maxfee.
- Setting `startpremium = 0` means starting bid = basefee.

![](fixedesc.jpeg)
_Bid in solid purple line, basefee in blue._

### Pros/cons

#### Pros

- Respects intuition of `basefee` as good default current price + escalating tip.
- For stable `basefee`, looks like escalator with a well-defined `startbid`.

#### Cons

- Gas price can raise faster than the escalator would plan, if basefee increases faster than the escalator slope. Should the premium follow? See "floating escalator started on basefee".
- Cannot write EIP 1559 simple strategy basefee + fixed premium under that model.

## Floating escalator

**Intuition:** The "true" EIP 1559 with escalating tips. User specifies an escalator for the tip, which is added to the current basefee always, as opposed to the basefee at `startblock` for the fixed escalator. Users specifying a steeper escalator "take off" above other users, expressing their higher time preferences.

### User-specified parameters

- `startblock`
- `endblock`
- `startpremium`
- `maxfee` OR `maxpremium` OR both.

### Computed parameters

- If `maxfee` is given: `maxpremium = maxfee - (b[startblock] + startpremium)`
- If `maxpremium` is given: `maxfee = b[startblock] + maxpremium`
- If both are given, NA.

### Gas price

```python
gasprice[t] = min(
  b[t] + p[t],
  maxfee
)

# Include only if
assert gasprice[t] >= b[t]
```

Gas price set current basefee `b[t]` + current premium `p[t]`, bounded above by `maxfee`.

![](floatingesc.jpeg)
_Bid in solid purple line, basefee in blue._

### Pros/cons

#### Pros

- Respects intuition of `basefee` as good default current price + escalating tip.
- For stable `basefee`, looks like escalator with a well-defined `startbid`.
- For unstable `basefee`, escalates tip in excess of the current basefee, unlike the fixed escalator.
- Setting `startpremium = maxpremium` and some `maxfee`, this is equivalent to the EIP 1559 paradigm (with `endblock` far into the future).

![](floatingescfixedtip.jpeg)
_Bid in solid purple line, basefee in blue._

#### Cons

- "Double dynamics" of basefee varying + tip varying, maybe hard to reason about.
- You can reach your `maxfee` much faster than you intended if `basefee` increases during the transaction lifetime.
