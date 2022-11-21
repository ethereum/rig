---
title: 'Towards practical post quantum Single Secret Leader Election (SSLE) - Part 1'
description: 'Discussing a possible post quantum SSLE solution'
author: 'Antonio Sanso'
date: '2022-08-30'
---

## Introduction

[Single Secret Leader Election](https://eprint.iacr.org/2020/025.pdf) (*SSLE* from now on) is an important research problem the cryptographic community has been researching on. The *SSLE* protocols allow a set of users to elect a leader ensuring that the identity of the winner remains secret until he decides to reveal himself.
[Whisk](https://ethresear.ch/t/whisk-a-practical-shuffle-based-ssle-protocol-for-ethereum/11763) is a block proposer election protocol tailored to the Ethereum beacon chain that protects the privacy of proposers. It relies on discrete logarithm assumptions and uses a shuffling approach and NIZK proof of shuffle to prove correctness. 
This year [NIST announced](https://csrc.nist.gov/Projects/post-quantum-cryptography/selected-algorithms-2022) its choice for Post-Quantum-Cryptography algorithms that are going to replace the existing public key infrastructure ([Zhenfei Zhang](https://zhenfeizhang.github.io/material/aboutme/) covered this in a [previous blog post](https://crypto.ethereum.org/blog/nist-pqc-standard)).

In this blog post we are going to analyze a possible Post Quantum analogue of [Whisk](https://ethresear.ch/t/whisk-a-practical-shuffle-based-ssle-protocol-for-ethereum/11763) based on Commutative Supersingular isogenies (CSIDH).

**N.B.** If you wonder if this solution is affected by the new [devastating attack on SIDH](https://eprint.iacr.org/2022/975.pdf) the answer is **NO**. The Castryck-Decru Key Recovery Attack crucially relies on torsion point information that are not present in CSIDH based solutions. 

## Whisk's recap

As mentioned above  [Whisk](https://ethresear.ch/t/whisk-a-practical-shuffle-based-ssle-protocol-for-ethereum/11763) is a proposal to fully implement *SSLE* from `DDH`and `shuffles` scheme (see also section 6 from [Boneh et al paper](https://eprint.iacr.org/2020/025.pdf)).
The idea behind this solution is pretty straightforward and neat. Let's list below the key ingredients of the commitment scheme in Whisk (at the net of the shuffles):

1. Alice commits to a random long-term secret `k` using a tuple $(rG,krG)$ (called **tracker**). 
2. Bob randomizes Alice’s **tracker** with a random secret $z$ by multiplying both elements of the tuple: $(zrG,zkrG)$.
3. Alice proves ownership of her randomized tracker (i.e. open it) by providing a proof of knowledge of a discrete log (`DLOG NIZK`) that proves knowledge of a `k` such that $k(zrG)==zkrG$ .
4. Identity binding is achieved by having Alice provide a deterministic commitment $com(k)=kG$ when she registers her **tracker**.
5.  We also use it at registration and when opening the trackers to check that both the tracker and $com(k)$ use the same $k$ using a discrete log equivalence proof (`DLEQ NIZK`).

Whisk can be implemented in any group where the Decisional Diffie Hellman problem (DDH) is hard. Currently Whisk is instantiated via a commitment scheme in [BLS12-381](https://hackmd.io/@benjaminion/bls12-381).

## Commutative Supersingular isogenies (CSIDH).

This section (and the remainder of the blog post) will require some knowledge about elliptic curves and isogeny based cryptography. The general reference on elliptic curves is [Silverman](https://link.springer.com/book/10.1007/978-0-387-09494-6) for a thorough explanation of isogenies we refer to [De Feo](https://arxiv.org/pdf/1711.04062.pdf).

CSIDH is an isogeny based post quantum key exchange presented at [Asiacrypt 2018 ](10.1007/978-3-030-03332-3_15) based on an efficient commutative group action. The idea of using group actions based on isogenies finds its origins in the now well known [1997 paper by Couveignes](https://eprint.iacr.org/2006/291.pdf). Almost 10 years later Rostovtsev and Stolbunov [rediscovered Couveignes's ideas ](https://eprint.iacr.org/2006/145.pdf).

Couveignes in his seminal work introduced the concept of *Very Hard Homogeneous Spaces* (VHHS). A VHHS is a generalization of cyclic groups for which the computational and decisional Diffie-Hellman problem are hard. The exponentiation in the group (or the scalar multiplication if we use additive notation) is replaced by a group action on a set. The main hardness assumption underlying group actions based on isogenies, is that it is hard to invert the group action:

**Group Action Inverse Problem (GAIP)).** Given a curve $E$, with $End(E) = O$, find an ideal a ⊂ O such that $E = [a]E_0$.

The GAIP (also known as *vectorization*) might resemble a bit the discrete logarithm problem and in this blog post we exploit this analogy to translate the commitment scheme in Whisk to the CSIDH setting. 

## CSIDH Whisk 

In this section we will show that a 1:1 translation is indeed (almost) easily achievable. Indeed the translation from the DLOG setting to VHHS presents a caveat: in this blog post we will focus our attention on the *fraud proof version* of shuffle based *SSLE*. This is also described in the original SSLE paper (see **Removing NIZKs** paragraph). The reason behind this is because currently there isn't a way to have NIZK proof of shuffle based on isogenies. Apart from this, let's see how it is indeed possible to translate all the other ingredients. 

### Whisk commitment scheme

The hardness of the GAIP problem gives a natural translation of the Whish commitment scheme. Alice commits to a random long-term secret $[k]$ using a tuple $([r]E_0,[k][r]E_0)$, where $E_0:y^2 = x^3 + x$ over $F_p$ is the base curve (the equivalent of the generator $G$ in the elliptic curve based solution).
Also the randomization phase is trivial: Bob randomizes Alice’s **tracker** with a random secret $[z]$ by multiplying both elements of the tuple: $([z][r]E_0,[z][k][r]E_0)$.

### `DDH` and CSIDH

The next thing to address is ensuring DDH is a hard problem in CSIDH.

**Group-Action DDH** the Group-Action DDH assumption holds if the two distributions
$([a]E_0, [b]E_0, [a][b]E_0)$ and $([a]E_0, [b]E_0, [c]E_0)$ are computationally indistinguishable.

[Castryck et al](CSV20) showed that the DDH problem is easy in ideal-class-group actions when the class number is even. Such groups are therefore unsuited for the above construction. As a countermeasure to their attack, they suggest working with supersingular elliptic curves over Fp for $p ≡ 3 (mod 4)$, which is already the case for CSIDH. In that setting, the Group-Action DDH problem is conjectured to be hard.

### `DLOG NIZK` in CSIDH

A sigma protocol proving knowledge of a solution of a GAIP instance in zero knowledge has been described in original [Couveignes's paper](https://eprint.iacr.org/2006/291.pdf) and further analyzed in [Stolbunov'sPhD thesis](https://ntnuopen.ntnu.no/ntnu-xmlui/bitstream/handle/11250/262577/529395_FULLTEXT01.pdf). Two incarnations of these ideas in the CSIDH setting are [SeaSign](https://eprint.iacr.org/2018/824.pdf) and [CSI-FiSh](https://eprint.iacr.org/2019/498.pdf). The first paper ([SeaSign](https://eprint.iacr.org/2018/824.pdf)) uses *rejection sampling* (a technique successfully employed in lattice based cryptography) to prevent signatures from leaking the private key (a problem that occurs if a sigma protocol is performed naively). The same is achieved in the latter paper ([CSI-FiSh](https://eprint.iacr.org/2019/498.pdf)) computing the class group of the imaginary quadratic field used in the CSIDH-512 cryptosystem.

### `DLEQ NIZK` in CSIDH

A way to solve discrete log equivalence proof (DLEQ NIZK) in the CSIDH is provided in [Beullens et al.](https://eprint.iacr.org/2020/1323.pdf) section 2.4.

## Conclusion

In this blog post we briefly analyzed a possible replacement of **Whisk** in the Post Quantum setting. We achieved this employing the commutative supersingular isogeny (CSIDH) setting. We have seen that a direct translation from DLOG to VHHS is indeed possible with some limitations. The derived Post Quantum Whisk Protocol is restricted to the *fraud proof version* due the lack of NIZK proof of shuffle in the isogeny setting. The current [zero-knowledge proving system](https://ethresear.ch/t/provable-single-secret-leader-election/7971) is an adaptation of the [Bayer-Groth shuffle argument](http://www0.cs.ucl.ac.uk/staff/J.Groth/MinimalShuffle.pdf) but is currently out of reach for isogeny based cryptography. We hope this blog post stimulates researchers to look into this open problem.

## Acknowledgement

We would like to thank Ward Beullens, Dan Boneh, Luca De Feo and George Kadianakis for for fruitful discussions and comments.
