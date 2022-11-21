---
title: 'The Legendre PRF'
description: 'We are interested in how resistant the Legendre pseudo-random function is to key recovery attacks, as well as any other interesting results on the Legendre PRF.'
---

The Legendre pseudo-random function is a PRF that is extremely well suited for secure multi-party computation (MPC) and zero-knowledge proofs (ZKP) over arithmetic circuits.

For bounties on breaking the Legendre PRF, please see [bounties](/bounties/legendre-prf/algorithmic-bounties) for algorithmic bounties and [here](/bounties/legendre-prf/concrete-instance-bounties) for concrete key recovery puzzles.

The Legendre pseudo-random function is a one-bit PRF $$\mathbb{F}_p \rightarrow \{0,1\}$$ defined using the [Legendre symbol](https://en.wikipedia.org/wiki/Legendre_symbol):

$$
\displaystyle L\_{p, K}(x) = \left\lceil\frac{1}{2}\left( \left(\frac{K + x}{p}\right) + 1\right)\right\rceil
$$

There are also variants of Legendre PRF with a higher degree, which replaces $$K+x$$ above with a univariate polynomial $$f_K(x)$$ of degree two or more, where $$K$$ represents its coefficients.

## Suitability for MPC

Thanks to a result by Grassi et al. (2016), we know that this PRF can be evaluated very efficiently in arithmetic circuit multi-party computations (MPCs). Due to the multiplicative property of the Legendre symbol, a multiplication by a random square does not change the result of an evaluation. By additionally blinding with a random bit, the Legendre symbol can be evaluated using only three multiplications, two of which can be done offline (before the input is known).

To compute the Legendre symbol $$\left[\left(\frac{x}{p}\right)\right]$$ for an input $$[x]$$ (square brackets indicate a shared value):

1. Choose a quadratic non-residue $$\alpha$$

2. Pre-compute a random square $$[s^2]$$ and a random bit $$[b]$$

3. Open the value $$t \leftarrow \mathrm{Open}([x] [s^2]([b] + (1- [b]) \alpha) )$$

4. Compute $$u = \left(\frac{t}{p}\right)$$ on the open value $$t$$

5. The result of the computation is $$y = u (2 [b] -1 )$$

## Suitability for ZKP

Similarly, the evaluation of this PRF can be proved efficiently in ZKP over $$\mathbb{F}_{p}$$. Let $$n$$ be any quadratic nonresidue in $$\mathbb{F}_{p}$$. To validate $$L_{p, K}(x) = b$$ for $$x, b \in \mathbb{F}_p$$:

1. Prove in ZKP that $$b\cdot (1 - b) = 0$$

2. For $$b = 0$$, compute $$a = \sqrt{n(K + x)}$$; for $$b = 1$$, compute $$a = \sqrt{K + x}$$

3. Allocate $$a$$ as a witness to the ZKP protocol

4. Prove in ZKP that $$a^2 = ((1 - b)n + b)\cdot (K+x)$$

## Bounties

Because of its suitability for MPCs, the Legendre PRF is used in a construction for the Ethereum 2.0 protocol. In order to encourage research in this PRF, we announced some bounties at Crypto'19. See [bounties](/bounties/legendre-prf/algorithmic-bounties).

## Further reading

- On using the Legendre PRF as a proof of custody: [Ethresearch post](https://ethresear.ch/t/using-the-legendre-symbol-as-a-prf-for-the-proof-of-custody/5169)
- Concrete proof of custody construction (TBA)

### Research papers

- [Damgård, Ivan Bjerre: On The Randomness of Legendre and Jacobi Sequences (1988)](https://link.springer.com/content/pdf/10.1007%2F0-387-34799-2_13.pdf)
- [Lorenzo Grassi, Christian Rechberger, Dragos Rotaru, Peter Scholl, Nigel P. Smart: MPC-Friendly Symmetric Key Primitives (2016)](https://eprint.iacr.org/2016/542.pdf)
- [Alexander Russell, Igor Shparlinski: Classical and Quantum Polynomial Reconstruction via Legendre Symbol Evaluation (2002)](https://arxiv.org/pdf/quant-ph/0212016.pdf)
- [Dmitry Khovratovich: Key recovery attacks on the Legendre PRFs within the birthday bound (2019)](https://eprint.iacr.org/2019/862.pdf)
- [Ward Beullens, Tim Beyne, Aleksei Udovenko, Giuseppe Vitto: Cryptanalysis of the Legendre PRF and generalizations (2019)](https://eprint.iacr.org/2019/1357.pdf)
- [Novak Kaluđerović, Thorsten Kleinjung and Dušan Kostić: Cryptanalysis of the generalised Legendre pseudorandom function (2020)](https://msp.org/obs/2020/4/p17.xhtml)

## Contact

[dankrad .at. ethereum .dot. org](mailto:dankrad%20.at.%20ethereum%20.dot.%20org)
