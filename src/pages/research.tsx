import { Text } from '@chakra-ui/react';
import { InlineMath } from 'react-katex';
import type { NextPage } from 'next';

import { PageMetadata, Publication, ResearchArea } from '../components/UI';

const Research: NextPage = () => {
  return (
    <>
      <PageMetadata
        title='Research'
        description='Explore the cryptography research and papers published by the Ethereum Foundation'
      />

      <main>
        <ResearchArea subtitle='Polynomial and vector commitments' mb={10}>
          <Publication
            title='Halo Infinite: Proof-Carrying Data from Additive Polynomial Commitments'
            authors='Dan Boneh, Justin Drake, Ben Fisch, Ariel Gabizon'
            conference={'Crypto 2021.'}
            link='https://eprint.iacr.org/2020/1536.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                Polynomial commitment schemes (PCS) have recently been in the spotlight for their
                key role in building SNARKs. A PCS provides the ability to commit to a polynomial
                over a finite field and prove its evaluation at points. A succinct PCS has
                commitment and evaluation proof size sublinear in the degree of the polynomial. An
                efficient PCS has sublinear proof verification. Any efficient and succinct PCS can
                be used to construct a SNARK with similar security and efficiency characteristics
                (in the random oracle model).
              </em>
            </Text>

            <Text fontSize='sm'>
              <em>
                Proof-carrying data (PCD) enables a set of parties to carry out an indefinitely long
                distributed computation where every step along the way is accompanied by a proof of
                correctness. It generalizes incrementally verifiable computation and can even be
                used to construct SNARKs. Until recently, however, the only known method for
                constructing PCD required expensive SNARK recursion. A system called Halo first
                demonstrated a new methodology for building PCD without SNARKs, exploiting an
                aggregation property of the Bulletproofs innerproduct argument. The construction was
                heuristic because it makes non-black-box use of a concrete instantiation of the
                Fiat-Shamir transform. We expand upon this methodology to show that PCD can be
                (heuristically) built from any homomorphic polynomial commitment scheme (PCS), even
                if the PCS evaluation proofs are neither succinct nor efficient. In fact, the Halo
                methodology extends to any PCS that has an even more general property, namely the
                ability to aggregate linear combinations of commitments into a new succinct
                commitment that can later be opened to this linear combination. Our results thus
                imply new constructions of SNARKs and PCD that were not previously described in the
                literature and serve as a blueprint for future constructions as well.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Aggregatable subvector commitments for stateless cryptocurrencies'
            authors='Alin Tomescu, Ittai Abraham, Vitalik Buterin, Justin Drake, Dankrad Feist, Dmitry
            Khovratovich'
            conference={'SCN 2020.'}
            link='https://eprint.iacr.org/2020/527.pdf'
          >
            <Text fontSize='sm'>
              <em>
                An aggregatable subvector commitment (aSVC) scheme is a vector commitment (VC)
                scheme that can aggregate multiple proofs into a single, small subvector proof. In
                this paper, we formalize aSVCs and give a construction from constant-sized
                polynomial commitments. Our construction is unique in that it has linear-sized
                public parameters, it can compute all constant-sized proofs in quasilinear time, it
                updates proofs in constant time and it can aggregate multiple proofs into a
                constant-sized subvector proof. Furthermore, our concrete proof sizes are small due
                to our use of pairing-friendly groups. We use our aSVC to obtain a payments-only
                stateless cryptocurrency with very low communication and computation overheads.
                Specifically, our constant-sized, aggregatable proofs reduce each block&apos;s proof
                overhead to a single group element, which is optimal. Furthermore, our subvector
                proofs speed up block verification and our smaller public parameters further reduce
                block size.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Efficient polynomial commitment schemes for multiple points and polynomials'
            authors='Dan Boneh, Justin Drake, Ben Fisch, Ariel Gabizon'
            conference={'2020.'}
            link='https://eprint.iacr.org/2020/081.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                We present an enhanced version of the Kate, Zaverucha and Goldberg polynomial
                commitment scheme [KZG10] where a single group element can be an opening proof for
                multiple polynomials each evaluated at a different arbitrary subset of points.
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                As a sample application we “plug in” this scheme into the PLONK proving
                system[GWC19] to obtain improved proof size and prover run time at the expense of
                additional verifier G2 operations and pairings, and additional G2 SRS elements.
              </em>
            </Text>

            <Text fontSize='sm'>
              <em>
                We also present a second scheme where the proof consists of two group elements and
                the verifier complexity is better than previously known batched verification methods
                for [KZG10].
              </em>
            </Text>
          </Publication>
        </ResearchArea>

        <ResearchArea subtitle='Verifiable delay functions and random beacons' mb={10}>
          <Publication
            title='Not So Slowth: Invertible VDF for Ethereum and others'
            authors='Dmitry Khovratovich, Mary Maller, Pratyush Ranjan Tiwari'
            conference={'2021.'}
            link='https://khovratovich.github.io/MinRoot/minroot.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                We give a protocol for Asynchronous Distributed Key Generation (A-DKG) that is
                optimally resilient (can withstand {<InlineMath math={'f \\leq n/3'} />} faulty
                parties), has a constant expected number of rounds, has{' '}
                {<InlineMath math={'\\tilde{\\mathcal{O}}(n^3)'} />} expected communication
                complexity, and assumes only the existence of a PKI. Prior to our work, the best
                A-DKG protocols required {<InlineMath math={'\\Omega(n)'} />} expected number of
                rounds, and {<InlineMath math={'\\Omega(n^4)'} />} expected communication.
              </em>
            </Text>

            <Text fontSize='sm'>
              <em>
                Our A-DKG protocol relies on several building blocks that are of independent
                interest. We define and design a Proposal Election (PE) protocol that allows parties
                to retrospectively agree on a valid proposal after enough proposals have been sent
                from different parties. With constant probability the elected proposal was proposed
                by a nonfaulty party. In building our PE protocol, we design a Verifiable Gather
                protocol which allows parties to communicate which proposals they have and have not
                seen in a verifiable manner. The final building block to our A-DKG is a Validated
                Asynchronous Byzantine Agreement (VABA) protocol. We use our PE protocol to
                construct a VABA protocol that does not require leaders or an asynchronous DKG
                setup. Our VABA protocol can be used more generally when it is not possible to use
                threshold signatures.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Aggregatable Distributed Key Generation'
            authors='Kobi Gurkan, Philipp Jovanovic, Mary Maller, Sarah Meiklejohn, Gilad Stern, Alin
            Tomescu'
            conference={'Eurocrypt 2021.'}
            link='https://eprint.iacr.org/2021/005.pdf'
          >
            <Text fontSize='sm'>
              <em>
                In this paper, we introduce a distributed key generation (DKG) protocol with
                aggregatable and publicly-verifiable transcripts. Compared with prior
                publicly-verifiable approaches, our DKG reduces the size of the final transcript and
                the time to verify it from {<InlineMath math={'\\mathcal{O}(n^2)'} />} to{' '}
                {<InlineMath math={'\\mathcal{O}(n \\log n)'} />}, where n denotes the number of
                parties. As compared with prior non-publicly-verifiable approaches, our DKG
                leverages gossip rather than all-to-all communication to reduce verification and
                communication complexity. We also revisit existing DKG security definitions, which
                are quite strong, and propose new and natural relaxations. As a result, we can prove
                the security of our aggregatable DKG as well as that of several existing DKGs,
                including the popular Pedersen variant. We show that, under these new definitions,
                these existing DKGs can be used to yield secure threshold variants of popular
                cryptosystems such as El-Gamal encryption and BLS signatures. We also prove that our
                DKG can be securely combined with a new efficient verifiable unpredictable function
                (VUF), whose security we prove in the random oracle model. Finally, we
                experimentally evaluate our DKG and show that the perparty overheads scale linearly
                and are practical. For 64 parties, it takes 71 ms to share and 359 ms to verify the
                overall transcript, while for 8192 parties, it takes 8 s and 42.2 s respectively.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Verifiable Delay Functions from Supersingular Isogenies and Pairings'
            authors='Luca De Feo, Simon Masson, Christophe Petit, Antonio Sanso'
            conference={'Asiacrypt 2019.'}
            link='https://eprint.iacr.org/2019/166.pdf'
          >
            <Text fontSize='sm'>
              <em>
                We present two new Verifiable Delay Functions (VDF) based on assumptions from
                elliptic curve cryptography. We discuss both the advantages and some drawbacks of
                our constructions, we study their security and we demonstrate their practicality
                with a proof-of-concept implementation.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Post-Quantum Verifiable Random Function from Symmetric Primitives in PoS Blockchain'
            authors='Maxime Buser, Rafael Dowsley, Muhammed F. Esgin, Shabnam Kasra Kermanshahi, Veronika Kuchta, Joseph K. Liu, Raphael Phan, and Zhenfei Zhang'
            conference={'ESORICS 2022.'}
            link='https://eprint.iacr.org/2021/302.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
              Verifiable Random Functions (VRFs) play a key role in Proof-of-Stake blockchains 
              such as Algorand to achieve highly scalable consensus, but currently deployed VRFs 
              lack post-quantum security, which is crucial for future-readiness of blockchain systems. 
              This work presents the first quantum-safe VRF scheme based on symmetric primitives. 
              Our main proposal is a practical many-time quantum-safe VRF construction, X-VRF, 
              based on the XMSS signature scheme. An innovation of our work is to use the state of 
              the blockchain to counter the undesired stateful nature of XMSS by constructing a 
              blockchain-empowered VRF. While increasing the usability of XMSS, our technique also 
              enforces honest behavior when creating an X-VRF output so as to satisfy the fundamental 
              uniqueness property of VRFs. We show how X-VRF can be used in the Algorand setting to 
              extend it to a quantum-safe blockchain and provide four instances of X-VRF with different 
              key life-time. Our extensive performance evaluation, analysis and implementation indicate 
              the effectiveness of our proposed constructions in practice. Particularly, we demonstrate 
              that X-VRF is the most efficient quantum-safe VRF with a maximum proof size of 3 KB and 
              a possible TPS of 449 for a network of thousand nodes.
              </em>
            </Text>
          </Publication>
        </ResearchArea>

        <ResearchArea subtitle='Zero-Knowledge Proofs' mb={10}>
          <Publication
            title='SnarkPack: Practical SNARK Aggregation'
            authors='Nicolas Gailly, Mary Maller, Anca Nitulescu'
            conference={'FC 2022.'}
            link='https://eprint.iacr.org/2021/529.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                Zero-knowledge SNARKs (zk-SNARKs) are non-interactive proof systems with short and
                efficiently verifiable proofs that do not reveal anything more than the correctness
                of the statement. zk-SNARKs are widely used in decentralised systems to address
                privacy and scalability concerns.
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                A major drawback of such proof systems in practice is the requirement to run a
                trusted setup for the public parameters. Moreover, these parameters set an upper
                bound to the size of the computations or statements to be proven, which results in
                new scalability problems.
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                We design and implement SnarkPack, a new argument that further reduces the size of
                SNARK proofs by means of aggregation. Our goal is to provide an off-the-shelf
                solution that is practical in the following sense: (1) it is compatible with
                existing deployed SNARK systems, (2) it does not require any extra trusted setup.
                SnarkPack is designed to work with Groth16 scheme and has logarithmic size proofs
                and a verifier that runs in logarithmic time in the number of proofs to be
                aggregated. Most importantly, SnarkPack reuses the public parameters from Groth16
                system.
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                SnarkPack can aggregate 8192 proofs in 8.7s and verify them in 163ms, yielding a
                verification mechanism that is exponentially faster than other solutions. SnarkPack
                can be used in blockchain applications that rely on many SNARK proofs such as
                Proof-of-Space or roll-up solutions.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Proofs for inner pairing products and applications'
            authors='Benedikt Bünz, Mary Maller, Pratyush Mishra, Nirvan Tyagi, Psi Vesely'
            conference={'Asiacrypt 2021.'}
            link='https://eprint.iacr.org/2019/1177.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                We present a generalized inner product argument and demonstrate its applications to
                pairing-based languages. We apply our generalized argument to proving that an inner
                pairing product is correctly evaluated with respect to committed vectors of n source
                group elements. With a structured reference string (SRS), we achieve a
                logarithmic-time verifier whose work is dominated by 6 log n target group
                exponentiations. Proofs are of size 6 log n target group elements, computed using 6n
                pairings and 4n exponentiations in each source group. We apply our inner product
                arguments to build the first polynomial commitment scheme with succinct
                (logarithmic) verification,
                {<InlineMath math={'\\mathcal{O}(\\sqrt{d})'} />} prover complexity for degree{' '}
                {<InlineMath math={'d'} />} polynomials (not including the cost to evaluate the
                polynomial), and a CRS of size {<InlineMath math={'\\mathcal{O}(\\sqrt{d})'} />}.
                Concretely, this means that for d = 228, producing an evaluation proof in our
                protocol is 76
                {<InlineMath math={'\\times'} />} faster than doing so in the KZG [KZG10] commitment
                scheme, and the CRS in our protocol is 1,000
                {<InlineMath math={'\\times'} />} smaller: 13MB vs 13GB for KZG. This gap only grows
                as the degree increases. Our polynomial commitment scheme is applicable to both
                univariate and bivariate polynomials.
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                As a second application, we introduce an argument for aggregating n Groth16 zkSNARKs
                into an {<InlineMath math={'\\mathcal{O}(\\log n)'} />} sized proof. Our protocol is
                significantly more efficient than aggregating these SNARKs via recursive composition
                [BCGMMW20]: we can aggregate about 130,000 proofs in 25min, while in the same time
                recursive composition aggregates just 90 proofs.
              </em>
            </Text>

            <Text fontSize='sm'>
              <em>
                Finally, we show how to apply our aggregation protocol to construct a low-memory
                SNARK for machine computations. For a computation that requires time T and space S,
                our SNARK produces proofs in space{' '}
                {<InlineMath math={'\\tilde{\\mathcal{O}}(S + T)'} />}, which is significantly more
                space efficient than a monolithic SNARK, which requires space{' '}
                {<InlineMath math={'\\tilde{\\mathcal{O}}(S \\cdot T)'} />}.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Snarky Ceremonies'
            authors='Markulf Kohlweiss, Mary Maller, Janno Siim, Mikhail Volkhov'
            conference={'Asiacrypt 2021.'}
            link='https://eprint.iacr.org/2021/219.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                Succinct non-interactive arguments of knowledge (SNARKs) have found numerous
                applications in the blockchain setting and elsewhere. The most efficient SNARKs
                require a distributed ceremony protocol to generate public parameters, also known as
                a structured reference string (SRS). Our contributions are two-fold:
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                &ndash; We give a security framework for non-interactive zero-knowledge arguments
                with a ceremony protocol.
              </em>
            </Text>

            <Text fontSize='sm'>
              <em>
                &ndash; We revisit the ceremony protocol of Groth&apos;s SNARK [Bowe et al., 2017].
                We show that the original construction can be simplified and optimized, and then
                prove its security in our new framework. Importantly, our construction avoids the
                random beacon model used in the original work.
              </em>
            </Text>
          </Publication>
        </ResearchArea>

        <ResearchArea subtitle='Hash Functions' mb={10}>
          <Publication
            title='T5: Hashing Five Inputs with Three Compression Calls'
            authors='Yevgeniy Dodis, Dmitry Khovratovich, Nicky Mouha, Mridul Nandi'
            conference={'ITC 2021.'}
            link='https://eprint.iacr.org/2021/373.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                We prove that this construction matches Stam’s bound, by providing{' '}
                {<InlineMath math={'\\tilde{\\mathcal{O}}(q^2 / 2^n)'} />} collision security and{' '}
                {<InlineMath math={'\\mathcal{O}(q^3 / 2^{2n} + nq/2^n)'} />} preimage security (the
                latter term dominates in the region of interest, when{' '}
                {<InlineMath math={'q \\leq 2^{n/2}'} />}). In particular, it provides birthday
                security for hashing 5 inputs using three 2n-to-n compression calls, instead of only
                4 inputs in prior constructions.
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                Thus, we get a sequential variant of the Merkle-Damgard (MD) hashing, where t
                message blocks are hashed using only {<InlineMath math={'3t/4'} />} calls to the
                2n-to-n compression functions; a 25% saving over traditional hash function
                constructions. This time reduces to {<InlineMath math={'t/4'} />} (resp.{' '}
                {<InlineMath math={'t/2'} />}) sequential calls using 3 (resp. 2) parallel execution
                units; saving a factor of 4 (resp. 2) over the traditional MD-hashing, where
                parallelism does not help to process one message.
              </em>
            </Text>

            <Text mb={4} fontSize='sm'>
              <em>
                We also get a novel variant of a Merkle tree, where t message blocks can be
                processed using 0.75({<InlineMath math={'t'} />} &minus; 1) compression function
                calls and depth {<InlineMath math={'0.86 \\log_2 t'} />}, thereby saving 25% in the
                number of calls and 14% in the update time over Merkle trees. We provide two modes
                for a local opening of a particular message block: conservative and aggressive. The
                former retains the birthday security, but provides longer proofs and local
                verification time than the traditional Merkle tree.
              </em>
            </Text>

            <Text fontSize='sm'>
              <em>
                For the aggressive variant, we reduce the proof length to a 29% overhead compared to
                Merkle trees ({<InlineMath math={'1.29 \\log_2 t'} />} vs{' '}
                {<InlineMath math={'\\log_2 t'} />}), but the verification time is now 14% faster (
                {<InlineMath math={'0.86 \\log_2 t'} />} vs {<InlineMath math={'\\log_2 t'} />}
                ). However, birthday security is only shown under a plausible conjecture related to
                the 3-XOR problem, and only for the (common, but not universal) setting where the
                root of the Merkle tree is known to correspond to a valid t-block message.
              </em>
            </Text>
          </Publication>
        </ResearchArea>

        <ResearchArea subtitle='Miscellaneous'>
          <Publication
            title='How to Prove Schnorr Assuming Schnorr: Security of Multi-and Threshold Signatures'
            authors='Elizabeth Crites, Chelsea Komlo, Mary Maller'
            conference={'2021.'}
            link='https://eprint.iacr.org/2021/1375.pdf'
          >
            <Text mb={4} fontSize='sm'>
              <em>
                In this paper, we present new techniques for proving the security of multi- and
                threshold signature schemes under discrete logarithm assumptions in the random
                oracle model. The purpose is to provide a simple framework for analyzing the
                relatively complex interactions of these schemes in a concurrent model, thereby
                reducing the risk of attacks. We make use of proofs of possession and prove that a
                Schnorr signature suffices as a proof of possession in the algebraic group model
                without any tightness loss. We introduce and prove the security of a simple,
                three-round multisignature SimpleMuSig.
              </em>
            </Text>

            <Text fontSize='sm'>
              <em>
                Using our new techniques, we prove the concurrent security of a variant of the
                MuSig2 multisignature scheme that includes proofs of possession as well as the FROST
                threshold signature scheme. These are currently the most efficient schemes in the
                literature for generating Schnorr signatures in a multiparty setting. Our variant of
                MuSig2, which we call SpeedyMuSig, has faster key aggregation due to the proofs of
                possession.
              </em>
            </Text>
          </Publication>

          <Publication
            title='Reputable List Curation from Decentralized Voting'
            authors='Elizabeth Crites, Mary Maller, Sarah Meiklejohn, Rebekah Mercer'
            conference={'PETS 2020.'}
            link='https://eprint.iacr.org/2020/709.pdf'
          >
            <Text fontSize='sm'>
              <em>
                Token-curated registries (TCRs) are a mechanism by which a set of users are able to
                jointly curate a reputable list about real-world information. Entries in the
                registry may have any form, so this primitive has been proposed for use— and
                deployed— in a variety of decentralized applications, ranging from the simple joint
                creation of lists to helping to prevent the spread of misinformation online. Despite
                this interest, the security of this primitive is not well understood, and indeed
                existing constructions do not achieve strong or provable notions of security or
                privacy. In this paper, we provide a formal cryptographic treatment of TCRs as well
                as a construction that provably hides the votes cast by individual curators. Along
                the way, we provide a model and proof of security for an underlying voting scheme,
                which may be of independent interest.
              </em>
            </Text>
          </Publication>
        </ResearchArea>
      </main>
    </>
  );
};

export default Research;
