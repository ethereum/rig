---
title: 'MiMC Hash Challenge Bounty'
description: 'Rewards for finding collisions in MiMCSponge, a sponge construction instantiated with MiMC-Feistel over a prime field, targeting 128-bit and 80-bit security.'
---

The [Ethereum Foundation](https://ethereum.org/en/) and [Protocol Labs](https://protocol.ai/) are offering rewards for finding collisions in MiMCSponge, a [sponge construction](https://en.wikipedia.org/wiki/Sponge_function) instantiated with MiMC-Feistel over a prime field, targeting 128-bit and 80-bit security, on one of two fields described below.

## Introduction

In 2017 Ethereum added support for BN254, a pairing-friendly elliptic-curve, via the [Byzantium hard-fork](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-609.md), making it possible to verify SNARKs in a smart contract. Many applications use hashes both inside SNARKs and in smart contracts, calling for a hash function that is efficient in both cases.

Protocol Labs are using BLS12-381, a pairing-friendly elliptic-curve introduced by the ECC team.

MiMC has been initially introduced in a [paper from 2016](https://eprint.iacr.org/2016/492.pdf), as a cryptographic primitive with low multiplicative complexity, making it attractive for SNARKs, such as [Groth16](https://eprint.iacr.org/2016/260.pdf). One particular use of interest is a hash function based on a sponge construction instantiated with MiMC-Feistel permutation over a prime field.

While more low multiplicative complexity hash function have been published, MiMC is the earliest of the bunch and is already used in some applications on Ethereum.

## Challenge Details

Rewards will be given for the following results:

| Result                                                                                     | Reward  |
| ------------------------------------------------------------------------------------------ | ------- |
| Collisions on the proposed 220 rounds, on either of the fields, targeting 128-bit security | $20,000 |
| Collisions on the proposed 220 rounds, on either of the fields, targeting 128-bit security | $20,000 |

### BN254

| Parameter   | Value                                                                         |
| ----------- | ----------------------------------------------------------------------------- |
| Field prime | 21888242871839275222246405745257275088548364400416034343698204186575808495617 |
| Rounds      | 220                                                                           |
| Exponent    | 5                                                                             |
| r           | 1                                                                             |
| c           | 1                                                                             |

### BLS12-381

| Parameter   | Value                                                                         |
| ----------- | ----------------------------------------------------------------------------- |
| Field prime | 52435875175126190479447740508185965837690552500527637822603658699938581184513 |
| Rounds      | 220                                                                           |
| Exponent    | 5                                                                             |
| r           | 1                                                                             |
| c           | 1                                                                             |

## Reference code

Reference code for MiMCSponge on BN254 exists in the [circomlib](https://github.com/iden3/circomlibjs/blob/5164544558570f934d72d40c70779fc745350a0e/src/mimcsponge.js) code base, where the constants for the hash are generated using [this code](https://github.com/iden3/circomlibjs/blob/5164544558570f934d72d40c70779fc745350a0e/src/mimcsponge_printconstants.js). Participants are also encouraged to examine the [MiMCSponge circuit code](https://github.com/iden3/circomlib/blob/master/circuits/mimcsponge.circom), the [MiMC-Feistel EVM bytecode](https://github.com/iden3/circomlibjs/blob/5164544558570f934d72d40c70779fc745350a0e/src/mimcsponge_gencontract.js) and the MiMCSponge Solidity code. Rewards for significant bugs in these may also be offered.

## Submissions

Submissions should be sent to [mimc-challenge@ethereum.org](mailto:mimc-challenge@ethereum.org), and rewards will be given in USD, ETH or DAI. Submissions can not be anonymous.
