---
title: 'Legendre PRF algorithmic Bounties'
description: 'Bounties on breaking the Legendre PRF.'
---

## The Legendre PRF

The Legendre pseudo-random function is a one-bit PRF $$\mathbb{F}_p \rightarrow \{0,1\}$$ defined using the Legendre symbol:

$$
\displaystyle L\_{p, K}(x) = \left\lceil\frac{1}{2}\left( \left(\frac{K + x}{p}\right) + 1\right)\right\rceil
$$

## Bounties

### $ 20,000

&nbsp;&nbsp;For either

- a sub-exponential, i.e. $$2^{(\log p)^c}$$ for some $$0<c<1$$, classical key recovery algorithm that extracts the key $$K$$ using inputs chosen by the attacker[^1]
- a security proof which reduces the Legendre pseudo-random function distinguishing problem to a well-known computational hardness assumption (see below)

### $ 6,000

&nbsp;&nbsp;For a classical key recovery algorithm improving on the algorithm by Kaluđerović, Kleinjung and Kostić ($$ O (p \log(p) \log(\log(p))/M^2)$$ Legendre evaluations where $$M$$ is the number of PRF queries needed) algorithm by more than a polylog[^3] factor, using a sub-exponential, i.e. $$M=2^{(\log p)^c}$$ for $$0<c<1$$ number of queries.[^1] [^2]

### $ 3,000

&nbsp;&nbsp;For a classical PRF distinguishing algorithm against the Legendre PRF that has an error probability bounded away from $$1/3$$ and is faster than direct use of the Kaluđerović, Kleinjung, and Kostić key recovery attacks, by more than a polylog factor[^3], using a sub-exponential, i.e. $$M = 2^{(\log p )^c}$$ for 0 < c < 1 number of queries.

[^1]: In all cases, probabilistic algorithms are also considered if they improve on the probabilistic versions of the known algorithms. Only classical (non-quantum) algorithms are permitted for the algorithm bounties.
[^2]: For this bounty, we also consider any algorithm that can distinguish a $$2^{(\log p)^c}$$ bit length output of the Legendre PRF from a random bit string with advantage $$>0.1$$
[^3]: An improvement $$g(n)$$ on a function $$f(n)$$ is by more than a polylog factor if $$f(n)/g(n)=\Omega(\log^m(n))$$ for all $$m\in\mathbf{N}$$.

The first two bounties are for the first entry that beats the given bounds. Please send submissions to Dankrad Feist ([dankrad .at. ethereum .dot. org](mailto:dankrad%20.at.%20ethereum%20.dot.%20org)).

## Computational hardness assumptions

For the reduction to a well-established computational hardness assumption, we consider the assumptions below which are taken from the [Wikipedia page](https://en.wikipedia.org/wiki/Computational_hardness_assumption)

- Integer factorization problem
- RSA problem
- Quadratic residuosity, higher residuosity and decisional composite residuosity problem
- Phi-hiding assumption
- Discrete logarithm, Diffie-Hellman and Decisional Diffie-Hellman in $$\mathbb{F}_p^{\times}$$
- Lattice problems: Shortest vector and learning with errors

## Concrete instances

At Devcon5, further bounties for concrete instances of the Legendre PRF were announced. For primes of size 64--148 (security levels 24--108[^5]), the following bounties are now available for recovering a Legendre key:

| Prime size | Security | Prize  | Status  |
| ---------- | -------- | ------ | ------- |
| 64 bits    | 24 bits  | 1 ETH  | CLAIMED |
| 74 bits    | 34 bits  | 2 ETH  | CLAIMED |
| 84 bits    | 44 bits  | 4 ETH  | CLAIMED |
| 100 bits   | 60 bits  | 8 ETH  |         |
| 148 bits   | 108 bits | 16 ETH |         |

For each of the challenges, $$2^{20}$$ bits of output from the Legendre PRF are available [here](/bounties/legendre-prf/concrete-instance-bounties). To claim one of these bounties, you must find the correct key that generates the outputs.

[^5]: This was originally set as 44--128 bits of security, but has been reduced to 24--108 due to the Beullens algorithm.

### Research papers

- [Damgård, Ivan Bjerre: On The Randomness of Legendre and Jacobi Sequences (1988)](https://link.springer.com/content/pdf/10.1007%2F0-387-34799-2_13.pdf)
- [Lorenzo Grassi, Christian Rechberger, Dragos Rotaru, Peter Scholl, Nigel P. Smart: MPC-Friendly Symmetric Key Primitives (2016)](https://eprint.iacr.org/2016/542.pdf)
- [Alexander Russell, Igor Shparlinski: Classical and Quantum Polynomial Reconstruction via Legendre Symbol Evaluation (2002)](https://arxiv.org/pdf/quant-ph/0212016.pdf)
- [Dmitry Khovratovich: Key recovery attacks on the Legendre PRFs within the birthday bound (2019)](https://eprint.iacr.org/2019/862.pdf)
- [Ward Beullens, Tim Beyne, Aleksei Udovenko, Giuseppe Vitto: Cryptanalysis of the Legendre PRF and generalizations (2019)](https://eprint.iacr.org/2019/1357.pdf)
- [Novak Kaluđerović, Thorsten Kleinjung and Dušan Kostić: Cryptanalysis of the generalised Legendre pseudorandom function (2020)](https://msp.org/obs/2020/4/p17.xhtml)
