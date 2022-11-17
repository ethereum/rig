---
title: 'Legendre PRF bounty smart contract instructions'
description: 'Bounties on breaking the Legendre PRF.'
---

If you have found the solution on one of our bounties on [Legendre instances](/bounties/legendre-prf/concrete-instance-bounties), here is how you can claim your bounty.

## Requirements

You need to have an Ethereum account with some Ether in it in order to pay for the gas needed by the contract. However, generally speaking, only quite a small amount is needed, and it should not cost more than a few Milliether.

## Claim process

A simple way to design a bounty contract is to just allow anyone with the correct solution to send a transaction and immediately get the bounty sent to their account. However, this is not safe: Assume that you want to claim a bounty and have found a correct solution. As soon as you broadcast your solution and until it is actually included in a block, anyone could create a transaction that uses your solution and claim the bounty for themselves. If they bid a higher gas price, then it is likely their transaction is included first, meaning they get the bounty, not you. This process is called front running.

That's why the Legendre bounty contract had to be built using a mechamism to prevent front running. It splits the redeeming process into two steps: "Claiming" and "redeeming".

Claiming a bounty works by submitting a `sha256(key, address)` value to the `claim_bounty` function. This does not reveal your solution (`key`) as it is hashed.

The contract will timestamp this and you will have to wait for 24 hours. Only then can you send your `key` to the `redeem_bounty` function. It will check that you have a correct claim for this bounty, and that it is a correct solution, and then transfer the bounty value to your account. At this point, anyone can see your solution, but lacking a correct claim for it, will not be able to redeem the bounty for at least another 25 hours, which will be enough time to safely redeem the bounty.

## Contract calls

`function claim_bounty(bytes32 claim_hash) public`

Call this function with a `sha256` hash of `key, address`, where `address` is the wallet/contract from which you want to claim the bounty (padded to 32 bytes) and `key` is the `uint256` value of your solution to the puzzle.

`function redeem_bounty(uint challenge_no, uint key) public`

Use this function to redeem the bounty, 24 hours after submitting your claim.

When calling this function, make sure to supply enough gas. Redeeming the bounties costs up to 1.5 million gas (for challenge 4), so test your call locally first and check how much gas it consumes.

For an example on how to call these functions, I also suggest looking at the calls made to redeem challenge 1: [claim_bounty()](https://etherscan.io/tx/0x6cbf7b49ba401721909e0a07bb18ac857ac9fe30595740c3a4fd74e5a78ccb61), [redeem_bounty()](https://etherscan.io/tx/0xb9ee411d12356bf56685283ca42f5c6b5b9b644d0b37bc2e729aa395eedb0ec8).

## Contract address/code

The address of the smart contract is [0x64af032181669383a370aE6e4b438ee26bB559b7](https://etherscan.io/address/0x64af032181669383a370ae6e4b438ee26bb559b7).

Code for playing with the contract and testing claim/redeem transactions can be found [here](https://github.com/dankrad/Legendre-bounty).

## Help

Email [dankrad .at. ethereum .dot. org](mailto:dankrad%20.at.%20ethereum%20.dot.%20org) if you need any help redeeming the bounties.
