---
title: 'ZK Hash Function Cryptanalysis Bounties'
description: 'Help us understand the security of new hash functions better.'
---

## Terms

**Task:** find $X1,X2,Y1,Y2$ such that $\displaystyle Perm(X1,X2,0)=(Y1,Y2,0)$

where $Perm$ is the inner sponge permutation (bijective mapping) of the hash function the challenge list.

- Solutions should be sent to [Dmitry Khovratovich](mailto:dmitry.khovratovich@ethereum.org) before November 30th 2022.
- First come first win.
- Within 1 month after the submission the authors should provide a technical report with the attack description, which should be released to the public domain at latest December 1st 2022. The code should be also made public before this date.
- **Total Bounty Budget:** $200,000 USD.
- Parameters are fixed on November 23rd 2021.

## Rescue Prime

[Design spec.](https://www.esat.kuleuven.be/cosic/publications/article-3259.pdf)

- $p=18446744073709551557 \text{\textasciitilde} 2^{64}$
- $m=3$
- $alpha=3$
- Number of rounds: $N$
- Brute force attack complexity: $2^{64}$

We expect that a variant with $s$ bits of security to withstand attacks of complexity up to $2^{1.5s}$ time (function calls) and memory.

[Reference implementation and bounty instances.](https://extgit.iaik.tugraz.at/krypto/zkfriendlyhashzoo/-/tree/master/bounties/src/rescue_prime)

| Category | Parameters        | Security Level (bits) | Bounty     |
| -------- | ----------------- | --------------------- | ---------- |
| ~~Easy~~ | $\sout{N=4, m=3}$ | ~~25~~                | ~~$2,000~~ |
| Easy     | $N=6, m=2$        | 25                    | $4,000     |
| Medium   | $N=7, m=2$        | 29                    | $6,000     |
| Hard     | $N=5, m=3$        | 30                    | $12,000    |
| Hard     | $N=8, m=2$        | 33                    | $26,000    |

## Feistel-MIMC

[Design spec.](https://eprint.iacr.org/2016/492.pdf)

- $p=18446744073709551557 \text{\textasciitilde} 2^{64}$
- $alpha=3$
- **Task:** find $X,Y$ such that $Feistel\text{\textendash}MiMC(X,0)=(Y,0)$
- Number of rounds: $r$
- Brute force attack complexity: $2^{64}$

We expect that a variant with $s$ bits of security to withstand attacks of complexity up to $2^{2s}$ time (function calls) and memory.

The initial parameters were broken and were replaced.

[Reference implementation and bounty instances.](https://extgit.iaik.tugraz.at/krypto/zkfriendlyhashzoo/-/tree/master/bounties/src/feistel_mimc)

| Category | Parameters        | Security Level (bits) | Bounty     |
| -------- | ----------------- | --------------------- | ---------- |
| ~~Easy~~ | $\sout{N=4, m=3}$ | ~~25~~                | ~~$2,000~~ |
| Easy     | $N=6, m=2$        | 25                    | $4,000     |
| Medium   | $N=7, m=2$        | 29                    | $6,000     |
| Hard     | $N=5, m=3$        | 30                    | $12,000    |
| Hard     | $N=8, m=2$        | 33                    | $26,000    |

## Poseidon

[Design spec.](https://eprint.iacr.org/2019/458.pdf)

- $p=18446744073709551557 \text{\textasciitilde} 2^{64}$
- $d=3$
- $t=3$
- Number of full rounds: $RF=8$
- Number of partial rounds $RP$ varies (see below)
- Brute force attack complexity: $2^{64}$

We expect that a variant with $s$ bits of security to withstand attacks of complexity up to $2^{s+37}$ time (function calls) and memory.

The initial parameters were broken and were replaced.

[Reference implementation and bounty instances.](https://extgit.iaik.tugraz.at/krypto/zkfriendlyhashzoo/-/tree/master/bounties/src/poseidon)

| Category   | Parameters     | Security Level (bits) | Bounty     |
| ---------- | -------------- | --------------------- | ---------- |
| ~~Easy~~   | $\sout{RP=3}$  | ~~8~~                 | ~~$2,000~~ |
| ~~Easy~~   | $\sout{RP=8}$  | ~~16~~                | ~~$4,000~~ |
| ~~Medium~~ | $\sout{RP=13}$ | ~~24~~                | ~~$6,000~~ |
| Hard       | $RP=19$        | 32                    | $12,000    |
| Hard       | $RP=24$        | 40                    | $26,000    |

## Reinforced Concrete

[Design spec.](https://eprint.iacr.org/2021/1038.pdf)

- Number of layers as in the original design
- Different prime field
- The best attack we have found for these variants is exhaustive search.
- Groebner basis challenges might be declared additionally.

We expect that a variant with $s$ bits of security to withstand attacks of complexity up to $2^{2s}$ time (function calls) and memory.

[Decomposition and alpha/beta values.](https://hackmd.io/l2JT8AQITJ2xRZpGErPnzA#Decomposition-parameters)

[Reference implementation and bounty instances.](https://extgit.iaik.tugraz.at/krypto/zkfriendlyhashzoo/-/tree/master/bounties/src/reinforced_concrete)

| Category | Parameters               | Security Level (bits) | Bounty  |
| -------- | ------------------------ | --------------------- | ------- |
| Easy     | $p=281474976710597$      | 24                    | $4,000  |
| Hard     | $p=72057594037926839$    | 28                    | $6,000  |
| Hard     | $p=18446744073709551557$ | 32                    | $12,000 |

## Contact

[dmitry.khovratovich@ethereum.org](mailto:dmitry.khovratovich@ethereum.org)
