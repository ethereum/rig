---
title: 'RSA Bounties'
description: 'Bounties for breaking RSA Assumptions.'
---

For more explanation on the assumptions, please see [RSA assumptions](/bounties/rsa/assumptions).

To improve the cryptanalysis of new RSA assumptions needed for Verifiable Delay Functions (VDFs), the Ethereum Foundation announced the following bounties at Real World Crypto 2020:

## Bounties

### $10,000

A bounty of $10,000 will be given for:

- An algorithm that solves the **Adaptive Root Problem** in an RSA group asymptotically faster than the fastest known algorithm for factoring an RSA number.[^1]
- Reducing the **Adaptive Root Assumption** to one of these assumptions: **Strong RSA Assumption**, **RSA Assumption**, **Diffie-Hellman Assumption**, or proving the Adaptive Root Assumption is (non-)equivalent to Factoring in the **Generic Ring Model**.

[^1]: At this point in time, the complexity of the General Number Field Sieve is $$L_n\left[\frac{1}{3}, \sqrt[3]{\frac{64}{9}}\right]$$.

## Assumptions

For more details on the assumptions, see here: [RSA Assumptions](/bounties/rsa/assumptions).

## Bounties for lower bounds on modular squaring

The RSA VDF depends critically on the sequentiality of modular squaring. To this end the [paper](https://eprint.iacr.org/2020/1461) by Williams and Wesolowski explored lower bounds in modular squaring, and announced the following bounties for improving them (please refer to the paper for details and definitions):

### $5,000

- Prove that for all $$n \geq 128$$, SUM on $$n$$-bit inputs requires depth at least $$c \log_2(n)$$ for some $$c > 2$$. (That is, improve upon Krapchenko's lower bound for **SUM**)

### $5,000

- Prove that for all $$n \geq 128$$, **SUM** on $$n$$-bit inputs requires depth at least $$4 \log_2(n)$$. (That is, prove the "reasonable hypothesis" stated immediately after Theorem 2 of the paper. This $$\$5,000$$ bounty is in addition to the $$\$5,000$$ bounty above.)

### $2,000

- Prove that there is a $$c < 4$$ such that for all $$n \geq 128$$, **SUM** has circuits of depth at most $$c \log_2(n)$$. (That is, refute the "reasonable hypothesis", and do so for all large enough input lengths $$n$$.)

### $3,000

- Improve the average-case depth lower bound Theorem 3 from the paper to $$c \log_2(n)$$ for some $$c > 1$$, for any algorithm computing **MS-MOD2** on at least $$51\%$$ of the inputs.

## Concrete instances

Bounties for solving the RSA adaptive root problem in concrete RSA groups have been instantiated on an Ethereum smart contract:

| Modulus (bits) | Bounty | Claimed |
| -------------- | ------ | ------- |
| 625            | 1 ETH  | YES     |
| 768            | 4 ETH  |         |
| 1024           | 8 ETH  |         |
| 2048           | 16 ETH |         |

For more details, see [concrete instance bounties](/bounties/rsa/concrete-instance-bounties).
