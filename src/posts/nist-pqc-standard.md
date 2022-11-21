---
title: 'NIST Post-Quantum-Cryptography Standardization Process and What it means for Ethereum'
description: 'Explaining NIST PQC standardization and its implications on Ethereum'
author: 'Zhenfei Zhang'
date: '2022-07-11'
---
## 1. Introduction
On July 5, 2022, the US National Institute of Standards and Technology (NIST) [announced](https://csrc.nist.gov/Projects/post-quantum-cryptography/selected-algorithms-2022) it will standardize four quantum-safe cryptography algorithms, including
- [Kyber](https://pq-crystals.org/kyber/), a lattice based public-key encryption (PKE) and key-establishment algorithm, 
- [Dilithium](https://pq-crystals.org/dilithium/), a lattice based digital signature scheme,
- [Falcon](https://falcon-sign.info/), another lattice based digital signature scheme,
- [SPHINCS+](https://sphincs.org/), a hash based digital signature scheme.

This _semi-concludes_ a half-decade long search for quantum-safe alternatives to existing public 
key infrastructure.

### 1.1 The so-called Quantum Apocalypse

Today, our entire public key infrastructure is built on top of two mathematical problems: integer factorization and discrete logarithm problems. When you open an HTTPS link, it runs the TLS protocol under the hood, which negotiates a session key via the Diffie-Hellman key exchange protocol over a certain elliptic curve group. Another example, a step closer to our blockchain community, when you make an ETH transfer, you sign your transaction with your secret key, using the ECDSA digital signature scheme. 

Almost 40 years ago, Peter Shor discovered [an algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm) that runs in linear time over a quantum computer, that finds the period of a given function. This result implies that both the integer factorization and the discrete logarithm problems are easy to solve with quantum computers, and hence, eliminate existing PKIs that we are using today. 

## 2. NIST's search for quantum-safe candidates

Although cryptographic research in quantum-safe cryptography is piloted back in 1960s, this space did not receive much attention till the winter of 2016, when NIST, the _de facto_ standard body to make cryptographic standards for almost the entire world, [publicly announced](https://csrc.nist.gov/Projects/post-quantum-cryptography/post-quantum-cryptography-standardization/Call-for-Proposals) its call for proposals for the quantum-safe cryptography solutions for both key establishment and digital signatures. A year later, NIST received [81 submissions](https://csrc.nist.gov/Projects/post-quantum-cryptography/post-quantum-cryptography-standardization/Round-1-Submissions) from academic thought leaders and industry pioneers, consists of the following 5 categories,
- [lattice based cryptography](https://en.wikipedia.org/wiki/Lattice-based_cryptography), for both PKEs and signatures;
- [code based cryptography](https://en.wikipedia.org/wiki/McEliece_cryptosystem), for PKEs;
- [multivariate cryptography](https://en.wikipedia.org/wiki/Multivariate_cryptography), for signatures;
- [hash based cryptography](https://en.wikipedia.org/wiki/Hash-based_cryptography), for signatures;
- [supersingular isogeny cryptography](https://en.wikipedia.org/wiki/Supersingular_isogeny_key_exchange), for PKEs.

The evaluation and cryptanalysis has began since then, with interesting modifications, breaks, fixes, and optimizations. In early 2019 and mid 2020, NIST announced their [2nd](https://csrc.nist.gov/Projects/post-quantum-cryptography/post-quantum-cryptography-standardization/round-2-submissions) and [3rd round](https://csrc.nist.gov/Projects/post-quantum-cryptography/post-quantum-cryptography-standardization/round-3-submissions) picks, reducing candidates from 81 to 26 then to 15. On July 5, 2022, NIST finally concluded the processes and chose to standardize [Kyber](https://pq-crystals.org/kyber/) for key establishment, [Dilithium](https://pq-crystals.org/dilithium/), [Falcon](https://falcon-sign.info/) and [SPHINCS+](https://sphincs.org/) for digital signatures.

As NIST remarked in [their own report](https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8413.pdf), the security of both Kyber and Dilithium are well understood; they both offer great performance and suit a wide range of applications. Falcon is based on a stronger assumption, and is an alternative to Dilithium in the use cases where signature sizes are sensitive. SPHINCS+ is ideal for users who are conservative in their trust assumptions because SPHINCS+ only relies on hash functions.

## 3. NIST's next steps

NIST plans to standardize both [Kyber](https://pq-crystals.org/kyber/) and [Dilithium](https://pq-crystals.org/dilithium/) first, followed by [Falcon](https://falcon-sign.info/) and [SPHINCS+](https://sphincs.org/). Each standard is expected to take roughly one year to complete. Changes in parameters are possible between the final standard and what is submitted to the 3rd round. 

In the meantime, note that the selected algorithms are build from lattices and hashes, while it is wise to standardize schemes from various of hardness assumptions, in case of breakthroughs in cryptanalytic research. NIST plans to take further actions in parallel with the standardization effort:

- NIST will started a [4th round](https://csrc.nist.gov/Projects/post-quantum-cryptography/round-4-submissions), analyzing key establishment schemes from code ([BIKE](https://bikesuite.org/), [classic McEliece](https://classic.mceliece.org) and [HQC](http://pqc-hqc.org/)) and supersingular isogeny ([SIKE](http://sike.org/));
- NIST will start a call for proposal for post-quantum signature schemes with a preference of neither lattice nor hash based construction.

## 4. What are the implications for Ethereum

First, it is safe to assume that there does not exist a general purpose quantum computer that is capable of breaking ECC as of today. There are various estimations of when or whether a quantum computer will arrive. This is out of the scope of this blog. Here we assume that we have sufficient time to deploy counter measures.

A natural question is __when do we need to be quantum ready__? In traditional world, it is advised to be quantum-safe as soon as possible due to the so-called _harvest-then-decrypt_ attacks, where an attacker may collect all the data sent over encrypted channels (for example, over TLS 1.3) and decrypt them when quantum computers become available. In the blockchain world, it becomes more severe if an application is required to store encrypted files on chain. However, for most use cases where cryptography is used for integrity or authenticity, it can wait a bit, since a future quantum attacker cannot come back in time and break the authenticity of today. This gives us some buffer time to study and deploy counter measures.

So, it becomes important to know the building blocks that are potentially vulnerable to quantum computers; and their quantum-safe alternatives.

### 4.1 Digital Signatures

Ethereum right now use ECDSA for authentication. As stated earlier, this is vulnerable to quantum attackers. We may switch to one of the above three quantum-safe signature schemes. We expect a (significant) decrease of performance due to the large size of signatures and public keys, listed below:

| | ECDSA | Dilithium | Falcon | SPHINCS+ |
| --- | ---: |---: |---: |---: |
| public key | 32 B| 1.3 KB | 897 B | 48 B |
| signature | 64 B| 2.4 KB | 666 B | 31 KB |

As one can see, the smallest quantum-safe signature scheme requires some 666 bytes for a signature, increased by 10x from 64 bytes as in ECDSA. We do not consider this to be scalable. Active research has been done in this domain to aggregate signatures, either natively or through a quantum-safe snark (more on this later). We may also hope for a new multivariate based signature scheme (which tend to have similar signature size as ECC, albeit a gigantic public key).

### 4.2 Verkle Tree

[Verkle tree](https://vitalik.ca/general/2021/06/18/verkle.html) is build on top of the Pedersen commitment scheme and Inner Product Arguments (IPAs), which assumes discrete logarithm is hard. There exist quantum-safe alternatives to vector commitments build on top of lattices, but all of the candidates perform a few magnitudes worse than ECC based solutions. Our best candidate thus far is to move back to [Merkle Patricia tree](https://ethereum.stackexchange.com/questions/6415/eli5-how-does-a-merkle-patricia-trie-tree-work) that only relies on the hash assumption.

### 4.3 Zero Knowledge Proofs and their applications

Zero knowledge proofs enable a large number of applications, ranging from [private transactions](https://z.cash/), [Verifiable Delay Function](https://eprint.iacr.org/2018/601.pdf), [single secret leader selection](https://ethresear.ch/t/whisk-a-practical-shuffle-based-ssle-protocol-for-ethereum/11763), [zk-rollups](https://ethresear.ch/t/zkopru-zk-optimistic-rollup-for-private-transactions/7717), [zkEVMs](https://ethresear.ch/t/the-intuition-and-summary-of-zkevm/10877) and more. There exist a various flavours of snark systems, split into two categories:
- pairing or elliptic curve based, such as Groth16, vanilla PLONK, Marlin, BulletProof, etc. 
- hash based, such as [Stark](https://eprint.iacr.org/2018/046.pdf) and [Plonky2](https://github.com/mir-protocol/plonky2).


The first category will be vulnerable to quantum computers.

Note that there are also lattice based constructions. Despite breakthrough works in the last few years, their performance is still multiple magnitude worse than hash based solutions, as of today.

Here we briefly mention two applications that will be essential for the proof of state consensus. For both applications, switching to a quantum-safe snark system such as [Stark](https://eprint.iacr.org/2018/046.pdf) or [Plonky2](https://github.com/mir-protocol/plonky2) results into solid solutions, although substantial work is needed to concretize the solutions. 




#### Verifiable Delay Function

The beacon chain used in proof of stake will use a [snark based VDF](https://zkproof.org/2021/11/24/practical-snark-based-vdf/) for validator and committee selection. The [current design](https://github.com/protocol/vdf) is to build it from the [Nova](https://eprint.iacr.org/2021/370) proof system which requires the discrete logarithm assumption. Replacing Nova with Stark or Plonky2 may be sufficient. In addition, we may use verifiable random functions, for which there are hash based and lattice based candidates.

#### Single secret leader selection

[Single secret leader selection](https://ethresear.ch/t/whisk-a-practical-shuffle-based-ssle-protocol-for-ethereum/11763) is used in a proof of stake protocol for block proposer selection. This is still an active research area. The major candidate under examination as of right now is [whisk](https://ethresear.ch/t/whisk-a-practical-shuffle-based-ssle-protocol-for-ethereum/11763) which uses a shuffling approach, and uses [an adaptation of the Bayer-Groth protocol](https://crypto.ethereum.org/blog/groth-sahai-blogpost) to prove shuffling correctness. This protocol relies on pairing and discrete logarithm assumptions. Switching to quantum-safe ZKPs will like decrease performance.

## 5. Conclusion

NIST's conclusion of its standardization process is our first step entering the quantum-safe world. It gives us semi-satisfactory replacements to the existing public key infrastructure, and implies NIST's strong confidence in hash and lattice based constructions, which will guide us to identify better and more scalable quantum-safe candidates for blockchain cryptography.

## Acknowledgement

We would like to thank Mary Maller for suggesting this blog; Mary and Dankrad Feist for feedbacks on earlier versions of this blog.