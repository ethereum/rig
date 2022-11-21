---
title: 'RSA assumptions'
description: 'Cash for RSA assumptions.'
---

![Relations between RSA assumptions](/images/bounties/RSA-ref.svg)

## Definitions

Most assumptions are formulated with respect to the security parameter $$\lambda$$. This means that the group parameters are selected so that the assumption holds with overwhelming probability as a function of $$\lambda$$ (for example, with $$1-\frac{1}{2^{\lambda}}$$). The set of parameters as a function of $$\lambda$$ is modelled as a group generator $$\mathrm{GGen}(\lambda)$$.

### RSA Assumption

The **RSA Assumption** states that no
efficient adversary can compute $$l$$-th roots a given random group element for a random $$l$$. Specifically,
it holds for $$\mathrm{GGen}$$ if for any probabilistic polynomial time adversary $$\mathcal{A}$$:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
u^l = w :
& (w,l)\xleftarrow{\$}\mathbb{G}\\
&u \xleftarrow{} \mathcal{A}(\mathbb{G},w,l)
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### Strong RSA Assumption

The **Strong RSA Assumption** states that no
efficient adversary can compute roots of a random group element. Specifically,
it holds for $$\mathrm{GGen}$$ if for any probabilistic polynomial time adversary $$\mathcal{A}$$:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
u^l = w,\; l>1 :
& w\xleftarrow{\$}\mathbb{G}\\
&(u,l) \xleftarrow{} \mathcal{A}(\mathbb{G},w)
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### QR-strong RSA Assumption

Let $$N$$ denote the RSA modulus and $$QR_N$$ being the set of quadratic residues (those that are squares of other elements) in $$\mathbb{Z}_N = \{0,1,2,\ldots,N-1\}$$.

The **QR-Strong RSA Assumption** states that no
efficient adversary can compute a root of a given random quadratic residue. Specifically,
it holds for $$\mathrm{GGen}$$ if for any probabilistic polynomial time adversary $$\mathcal{A}$$:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&Z_N\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
u^l = w,\; l>1 :
& w\xleftarrow{\$}QR_N\\
&(u,l) \xleftarrow{} \mathcal{A}(Z_N,w)
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### $$r$$-Strong RSA Assumption

The **$$r$$-Strong RSA Assumption** states that an
efficient adversary can compute at most $$r$$-th roots of a given random group element. Specifically,
it holds for $$\mathrm{GGen}$$ if for any probabilistic polynomial time adversary $$\mathcal{A}$$:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
u^l = w,\; l\neq r^k,\;k\in\mathbb{N} :
& w\xleftarrow{\$}\mathbb{G}\\
&(u,l) \xleftarrow{} \mathcal{A}(\mathbb{G},w)
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

Remarks:

- For $$r = 1$$ the definition is identical to the standard Strong RSA Assumption.
- For $$r = 2$$, the adversary
  is efficiently able to take square roots. In class groups of imaginary quadratic order taking
  square roots is easy[^1].
- In $$r$$-th order class groups taking $$r$$-th roots is easy[^1].

### Adaptive Root Assumption

The **Adaptive Root Assumption** holds for
$$\mathrm{GGen}$$ if there is no efficient adversary $$(\mathcal{A}_0, \mathcal{A}_1)$$ that succeeds in the following task. First,
$$\mathcal{A}_0$$ outputs an element $$w\in \mathbb{G}/\{-1, 1\}$$ and some state $$st$$. Then, a random prime in $$\mathrm{Primes}(\lambda)$$ is chosen
and $$\mathcal{A}_1(w,l,st)$$ outputs $$w^{1/l}\in\mathbb{G}/\{-1,1\}$$. For all efficient $$(\mathcal{A}_0, \mathcal{A}_1)$$:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
& (w,st)\xleftarrow{}\mathcal{A}_0(\mathbb{G})\\
u^l = w\neq 1 :& l\xleftarrow{\$}\Pi_{\lambda}=\mathrm{\mathrm{Pr}imes}(\lambda)\\
&u \xleftarrow{} \mathcal{A}_1(w,l,st)
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

Remarks:

- The number of primes in $$\Pi_{\lambda}$$ should be exponential in $$\lambda$$: it is possible to precompute $$w$$ using $$2^{\Pi_{\lambda}}$$ exponentiations. Then, an adversary with $$2^M$$ memory can store intermediate exponents and compute adaptive roots using $$2^{\Pi_{\lambda}-M}$$ exponentiations for each.

### Order assumption

The **Order assumption**. For any probabilistic polynomial time adversary $$\mathcal{A}$$ computing the order of a random element is hard:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
u^l = 1 : &u \xleftarrow{\$}\mathbb{G}\\
& l \xleftarrow{} \mathcal{A}(\mathbb{G})\\
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### Low Order Assumption

The **Low Order assumption**. For any probabilistic polynomial time adversary $$\mathcal{A}$$ finding any element of low order is hard:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
u^l = 1,\;u\not\in\{1,-1\} :
& (u,l) \xleftarrow{} \mathcal{A}(\mathbb{G})\\
& \text{and }l<2^{poly(\lambda)}
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### Fractional Root Assumption

The **Fractional Root assumption**. For any probabilistic polynomial time adversary $$\mathcal{A}$$

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
u^l = g^{a},\;l \nmid a : & g \xleftarrow{\$}\mathbb{G}\\
& (u,l,a) \xleftarrow{} \mathcal{A}(\mathbb{G},g)\\
& \text{and }a,l<2^{poly(\lambda)}
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### Diffie-Hellman Assumption

The **Diffie-Hellman Assumption** holds for
$$\mathrm{GGen}$$ if no efficient $$\mathcal{A}$$ can compute $$g^{ef}$$ from $$g,g^e,g^f$$ for random $$g,e,f$$:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
& (g,e,f)\xleftarrow{\$}\mathbb{G}\\
u = g^{ef} :& u \xleftarrow{} \mathcal{A}(g,g^e,g^f)
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### Discrete Logarithm

The **Discrete Logarithm** assumption
holds for
$$\mathrm{GGen}$$ if for all efficient $$\mathcal{A}$$:

$$
\displaystyle
\mathrm{Pr}
\begin{bmatrix}
&\mathbb{G}\xleftarrow{\$}\mathrm{GGen}(\lambda)\\
& (u,w)\xleftarrow{\$}\mathbb{G}\\
w = u^l :& l \xleftarrow{} \mathcal{A}(u,w)
\end{bmatrix}\leq \mathrm{negl}(\lambda)
$$

### Factoring

The **Factoring** assumption states that for random primes $$p,q$$ it is difficult to factor $$N=pq$$.

## Reductions and security

### Trivial reductions

- The Adaptive Root assumption implies the Low Order assumption. Indeed, for an element $$w$$ of order $$l$$ one can compute a $$q$$-th root by setting $$u = w^{q^{-1}\bmod{l}}$$.
- The Strong RSA assumption implies the RSA assumption (trivially).
- The Strong RSA assumption implies the QR-Strong assumption (almost trivial, due to the size of $$QR_N$$).
- For $$N=pq$$, where $$p \neq q$$ are safe primes, the Low Order assumption unconditionally holds in $$QR_N$$, because it contains no elements of low order.
- For an RSA modulus $$N$$, the Order assumption in the multiplicative group mod $$N$$ is equivalent to factoring.
- The Low Order assumption in the multiplicative group mod $$N$$ implies factoring in the case where $$l$$ is even and $$u^(l/2) /neq -1 (mod N)$$. Indeed, in this case, $$u^l-1$$ admits a non-trivial decomposition modulo N, which leads to factoring

### Nontrivial reductions

- The Factoring assumption implies the Discrete Logarithm assumption in an RSA group.[^2]
- The Strong RSA assumption is equivalent to the Fractional Root Assumption in the group of quadratic residues modulo $$N$$.[^3]

### Generic Group Model

A generic group algorithm is a program that performs only group operations and equality checks. The group is modelled as an oracle $$O$$, who knows the group order $$n$$, and a random function $$\sigma$$ that maps $$\mathbf{Z}_N$$ to bit strings, called the **encoding**. The algorithm input is $$\sigma(x_1),\sigma(x_2),\ldots,\sigma(x_k)$$. The algorithm can query the oracle on pairs $$(i,j)$$, and the oracle returns $$\sigma(x_i\pm x_j\pmod{n})$$. Equivalently, it computes $$\prod_{1\leq j \leq k}g_j^{a_j}$$ and informs about equal elements in results.

It is crucial that a generic group algorithm does not have access to the internal representation of group elements, which are integers in RSA.
Most RSA assumptions hold in the Generic Group Model.

- The Strong RSA assumption holds in the Generic Group Model.[^4]

This implies that the RSA assumption is hard too. The Factoring assumption can not be formulated in the Generic Group Model as the group size is unknown to the algorithm.

- The Adaptive Root assumption holds in the Generic Group Model.[^1]

However, these results give little insight to the actual security of RSA assumptions, as most existing RSA attacks use the integer form of the group elements. For example, computing the Jacobi symbol (see below) in an RSA group is easy despite being provably hard in the Generic Group Model.

### Generic Ring Model

Here we consider algorithms that are given the unit ring element $$1$$ and a single ring element $$x$$ as input and are supposed to output some element $$y$$. They can query the ring oracle using multiplication, division, and addition queries on the already known ring elements, and see if the oracle outputs a previously known element. Effectively these algorithms compute rational polynomial functions of $$x$$.

- If there is a generic ring algorithm that computes $$f(x)$$ such that $$f(x)\equiv 0 \bmod{n}$$ on a non-negligible fraction of points then one can derive a factoring algorithm.[^6]

- If there is an generic ring algorithm that breaks the Strong RSA assumption by outputting rational functions $$u=\frac{f(x)}{g(x)}$$ and $$l=\frac{h(x)}{q(x)}$$, then $$N$$ can be factored with the same complexity.[^7]

### Pseudo-freeness

Let $$A$$ be a set of constants and $$\mathcal{F}(A)$$ be the free group generated by $$A$$ i.e. the set of all finite products with multiples from $$A$$.

Let $$X$$ be a set of variables and consider equations of form $$w_1 = w_2$$ where $$w_1,w_2\in\mathcal{A}\cup \mathcal{X}$$, where $$\mathcal{A}$$ is a set of products of elements from $$A$$ and $$\mathcal{X}$$ is a a set of products of elements from $$X$$. A group $$G$$ is **pseudo-free** if no efficient adversary can find an equation that does not have solutions in $$\mathcal{F}(A)$$ and a solution to this equation in $$G$$ (i.e. where $$X$$ and $$A$$ are mapped to some elements of $$G$$), where the mapping from $$A$$ to $$G$$ is a random function, chosen for every run of the adversary.

Informally, a group is pseudo-free if no efficient algorithm can find a non-trivial relation among randomly chosen group elements. Recall that a **safe prime** $$p$$ has form $$p=2p'+1$$ where $$p'$$ is also prime. It is unknown if there are infinitely many safe primes.

- Assume that $$N$$ is the product of two safe primes. Then the Strong RSA assumption is equivalent to the RSA group being pseudo-free. [9, 10]

- The Order assumption holds in a pseudo-free group.[^8]

- The Diffie-Hellman assumption holds for a non-negligible fraction of bases $$g$$ in a pseudo-free group.[^9]

Therefore, the Strong RSA assumption implies the Order assumption if $$N$$ is the product of two safe primes. The situation when the Strong RSA assumption holds but the Adaptive Root assumption does not hold may thus only happen if the order of $$w$$ in the Adaptive Root assumption is unknown but roots are computable.

[^1]:
    Benedikt Bunz, Ben Fisch, and Alan Szepieniec. Transparent snarks from dark compilers. Cryptology
    ePrint Archive, Report 2019/1229, 2019. [https://eprint.iacr.org/2019/1229](https://eprint.iacr.org/2019/1229).

[^2]:
    Eric Bach. Discrete logarithms and factoring. Computer Science Division, University of California
    Berkeley, 1984. Available at [https://www2.eecs.berkeley.edu/Pubs/TechRpts/1984/CSD-84-186.pdf](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1984/CSD-84-186.pdf).

[^3]:
    Ronald Cramer and Victor Shoup. Signature schemes based on the strong RSA assumption. In ACM
    Conference on Computer and Communications Security, pages 46–51. ACM, 1999.

[^4]:
    Ivan Damgård and Maciej Koprowski. Generic lower bounds for root extraction and signature schemes
    in general groups. In EUROCRYPT, volume 2332 of Lecture Notes in Computer Science, pages 256--271. Springer, 2002.

[^5]:
    Divesh Aggarwal and Ueli M. Maurer. Breaking RSA generically is equivalent to factoring. In
    EUROCRYPT, volume 5479 of Lecture Notes in Computer Science, pages 36–53. Springer, 2009.

[^6]:
    Divesh Aggarwal, Ueli Maurer, and Igor Shparlinski. The equivalence of strong rsa and factoring in
    the generic ring model of computation. 2011. Available at [https://hal.inria.fr/inria-00607256/](https://hal.inria.fr/inria-00607256/)
    document.

[^7]:
    Daniele Micciancio. The RSA group is pseudo-free. In EUROCRYPT, volume 3494 of Lecture Notes
    in Computer Science, pages 387–403. Springer, 2005.

[^8]:
    Ronald L. Rivest. On the notion of pseudo-free groups. In TCC, volume 2951 of Lecture Notes in
    Computer Science, pages 505–521. Springer, 2004.

[^9]:
    Shingo Hasegawa, Shuji Isobe, Hiroki Shizuya, and Katsuhiro Tashiro. On the pseudo-freeness and
    the CDH assumption. Int. J. Inf. Sec., 8(5):347–355, 2009.
