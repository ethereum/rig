---
title: 'Groth-Sahai Proofs Are Not That Scary'
description: 'Groth-Sahai (GS) proofs are a zero-knowledge proving technique. We will walk through an example GS proof accessible to a general cryptographic audience.'
author: 'Mikhail Volkhov, Dimitris Kolonelos, Dmitry Khovratovich, Mary Maller'
date: '2022-06-06'
---

<p align="center"><img src="/images/posts/groth-sahai-explainer/armchairs.png" alt="Header image" width="800"/></p>

Groth-Sahai (GS) proofs are a zero-knowledge proving technique which can seem daunting to understand. This is because much of the literature attempts to generalise all possible things you can prove using GS techniques rather than because the proofs are overly complicated. In fact GS proofs are one of the simplest zero-knowledge constructions. For statements about group elements in pairing based groups, they are ideal because there is no heavy reduction to an NP constraint system, and this makes the prover very fast. Security wise they also rely on much more standard assumptions than SNARKs and thus are more likely to be secure.

In this post we will walk through an example Groth-Sahai proof and attempt to make the explanation accessible to a general cryptographic audience. Specifically we discuss how to prove that an ElGamal ciphertext contains $0$  or $1$.  Our example includes the improvements by Escala and Groth. Prerequisites include knowledge about what a zero-knowledge argument is and what Type-III pairings are (but not how they are constructed).

And for those interested in experimenting with GS proofs in practice we have written a simple [implementation in python](https://github.com/volhovm/groth-sahai-python) -- check it out! It includes both the example we will be going through in this paper, and the more general proving framework that you can use to construct proofs for your language.

## ElGamal in Pairing Product Equations

In order to prove that an ElGamal ciphertext contains $0$ or $1$ we must first *arithmetise* this statement into a form that is compatible with GS proofs. GS proofs take as input pairing-product equations; pairing product equations can be seen as the equivalent of arithmetic circuits in the sense that they arithmetise the relation that we are trying to prove. Thus in this section we show how to represent our statement using pairing product equations. In later sections we will show how to prove that these equations are satisfied under zero-knowledge.

## Notation and Pairings

Recall the standard property of pairings: $$ e(g^a,\widehat{h}^b) = e(g,\widehat{h})^{ab}$$ We denote the first source group by $\mathbb{G}_1$ and the second source group by  $\mathbb{G}_2$. Elements from $\mathbb{G}_2$ are denoted with wide hat like $\widehat{E}$. We will write $\Theta = g^{\theta}$ and $\widehat{D} = \widehat{h}^d$ trying, where it's possible, to use lowercase letters for exponents of the corresponding capital letter element.


Pairings allow us to define quadratic equations in the logarithms of the arguments, e.g. 
$$
\begin{array}{ccc}
e(X,\widehat{h})e(g,\widehat{Y})=1 & \Longleftrightarrow & \log_g X +\log_{\widehat{h}} \widehat{Y}=0 \\
e(X,\widehat{Y})=e(X',\widehat{Y}') & \Longleftrightarrow & \log_g X \cdot \log_{\widehat{h}} \widehat{Y} =\log_g X' \cdot \log_{\widehat{h}} \widehat{Y}'
\end{array}
$$
If you have not worked with pairings with multiple bases, see this explanation:
<details>
    <summary>Collapsible: On Pairings with Multible Bases</summary>

As later we will employ multiple bases and not just $g,\widehat{h}$, pairing equations will also work "in parallel" for all pairs of bases from $\mathbb{G}_1$ and $\mathbb{G}_2$.
Consider the following example.
By bilinearity of the pairing $e(g_1^a g_2^b, \widehat{h}_1^c \widehat{h}_2^d) = 1$ is equivalent to: $$ e(g_1,\widehat{h}_1)^{ac} \cdot e(g_1,\widehat{h}_2)^{ad} \cdot e(g_2,\widehat{h}_1)^{bc} \cdot e(g_2,\widehat{h}_2)^{bd} = 1 $$ In such a case we will always have $ac = ad = bc = bd = 0$ when all $g_i$ and $h_i$ are chosen independently and uniformly at random.

Here is an example of how it works:
<img src="/images/posts/groth-sahai-explainer/figure-4.png" alt="Pairings with Multiple Bases" width="700"/>


</details>


## ElGamal Verification in Pairing Equations

We first present our solution for arithmetising the statement "This ciphertext contains $0$ or $1$" directly and after explain the intuition for how we derived these equations. Let $g_1$ generate $\mathbb{G}_1$, and $\mathsf{pk} = g_1^\mathsf{sk}$. Consider a (lifted) ElGamal ciphertext 
$$
\mathsf{CT} = (\mathsf{CT}_1, \mathsf{CT}_2) = (g_1^r, M \cdot \mathsf{pk}^{r}) \tag{1}
$$ 
Then $M = g_1^m$ is either $(g_1)^0$ or $(g_1)^1$ if and only if there exist witnesses $\widehat{W}_1, W_2, \widehat{W}_3$ such that
$$
\begin{array}{r c l r } 
    e(\mathsf{CT}_1, \widehat{h}_1) & = & e(g_1 , \widehat{W}_1) & \hspace{1cm} (E_1)\\
    e(\mathsf{CT}_2, \widehat{h}_1) & = & e(\mathsf{pk}, \widehat{W}_1) e(W_2, \widehat{h}_1)  & (E_2)\\
    e(W_2, \widehat{h}_1) & = & e(g_1, \widehat{W}_3) & (E_3)\\
    e(W_2, \widehat{W}_3) & = & e(W_2, \widehat{h}_1) &  (E_4)
    \end{array}
$$
Note that the witness components $(\widehat{W}_1, W_2, \widehat{W}_3)$ must be kept secret because they reveal information about the message $M$.

Our purpose now is to explain how we arrived at the above set of pairing product equations and along the way to illustrate the design constraints that the GS proving system presents us with. Arithmetising statements is an art that Daira Hopwood is exceptionally skilled at (check out the Zcash spec, Appendix A, for many cool arithemetisation tricks). Alas, we are not Daira so please bear with us even if our solution is not optimal.

One characteristic feature of GS proofs is that all secret witness components must be group elements rather than field elements. So our secret that we want to keep hidden cannot be field elements $0$ or $1$ or $r$, but must instead be group elements $g_1^{0}$ or $g_1^1$ or $g_1^r$. For our ciphertext to encrypt $0$ or $1$ we thus desire that $m\in\{(g_1)^0,(g_1)^1\}$. Turning to the equation (1) we have that this condition that is equivalent to 
$$
\mathsf{CT}_2\cdot \mathsf{pk}^{-\log \mathsf{CT}_1} \in \{(g_1)^0,(g_1)^1\}\tag{2} 
$$ 
where logarithm is taken with base $g_1$. Denote $$ W_2 = g_1^{w_2} = \mathsf{CT}_2\cdot \mathsf{pk}^{-\log \mathsf{CT}_1} $$ We wish to check that $w_2^2-w_2 =0$. Our one and only method of checking constraints is using pairing equations. We cannot pair $W_2$ with itself because we can only pair $\mathbb{G}_1$ elements with $\mathbb{G}_2$ elements. Thus we choose to "bridge" $w_2$ into $\mathbb{G}_2$ by introducing an additional group element $\widehat{W}_3 = \widehat{h}_1^{\widehat{w}_3}$ such that
$$
\begin{array}{r c l}
w_2 & = & \widehat{w}_3 \\
w_2 \widehat{w}_3 - w_2 & = & 0
\end{array}
$$
where $w_2$ is a logarithm of some $\mathbb{G}_1$ element $W_2$ and $\widehat{w}_3$ is a logarithm of some $\mathbb{G}_2$ element $\widehat{W}_3$.

<img src="/images/posts/groth-sahai-explainer/figure-1.png" alt="Bridge illustration" width="600"/>

Then (2) is equivalent to
$$
\begin{array}{r c l}
\mathsf{CT}_2\cdot \mathsf{pk}^{-\log \mathsf{CT}_1}  & = & W_2 \tag{3}\\
e(W_2, \widehat{h}_1) & = & e(g_1, \widehat{W}_3)  \\
e(W_2, \widehat{W}_3) & = & e(W_2, \widehat{h}_1)
\end{array}
$$

That first condition in (3) that $\mathsf{CT}_2\cdot \mathsf{pk}^{-\log \mathsf{CT}_1} =W_2$ currently does not look very much like a pairing product equation. We cannot use logarithms in PPEs, so we need an alternative method for arithmetising that $$ \log \mathsf{CT}_2- \log \mathsf{CT}_1\cdot\log \mathsf{pk}=w_2 $$ As $\mathsf{CT}_1,\mathsf{CT}_2,\mathsf{pk}$ are all in $\mathbb{G}_1$, we make another bridge:
$$
\begin{array}{r c l}
\log_{g_1} \mathsf{CT}_1 & = & \widehat{w}_1\\
\log \mathsf{CT}_2-\log \mathsf{pk}\cdot \widehat{w}_1 & = & w_2
\end{array}
$$
In pairing equations this is equivalent to
$$
\begin{array}{r c l}
e(\mathsf{CT}_1, \widehat{h}_1) & = & e(g_1 , \widehat{W}_1) \\
e(\mathsf{CT}_2, \widehat{h}_1) & = & e(\mathsf{pk}, \widehat{W}_1) e(W_2, \widehat{h}_1)
\end{array}
$$
Combining all our pairing equations together we arrive at our final pairing product equation for arithmetising that $(\mathsf{CT}_1, \mathsf{CT}_2)$ encrypts $0$ or $1$.


## General Proof Structure
In this section we describe the GS setup, prover and the verifier used in representing the statement "This ciphertext encrypts $0$ or $1$".

### Transparent Setup

We discuss how to run the GS setup. The setup does not depend on our pairing product equations at all and the same setup is used for proving any statement. It is only the prover and the verifier that depend on the pairing product equation explicitly.

NIZK proofs are constructed with a common reference string (CRS), that is used for both producing and verifying proofs. In GS proofs the CRS is constructed using public randomness and therefore they are said to have a trustless setup (this is a positive thing because we do not have to trust a third party or MPC that replaces it, like with many SNARKs). The GS CRS consists of eight independent elements --- four in each group.
$$
\begin{array}{l}
g_1, g_2, g_3, g_4 \gets \mathbb{G}_1 \\
\widehat{h}_1, \widehat{h}_2, \widehat{h}_3, \widehat{h}_4 \gets \mathbb{G}_2 \\
\mathsf{crs} = (g_1 \ldots g_4, \widehat{h}_1 \ldots \widehat{h}_4)
\end{array}
$$ 
In practice these elements are typically sampled as the output of a hash function, and the seed is published so that anyone can verify the setup procedure. It is permitted and encouraged to have fun (not too much fun) when choosing the seed and we sometimes like to use the opening lines of famous books.

We will reuse the generator $g_1$ for our ElGamal ciphertext which helps us to simplify the structure of prover and verifier.


### Commitments to Witnesses

We now describe our GS prover. The prover aims to show the existence of a witness that satisfies the pairing product equations. The witness is secret and cannot be revealed directly. Thus instead the prover commits to the witness, and proves that the committed witness satisfies a related set of pairing product equations. We discuss the form of this commitment before we present the related set of equations.

The prover computes two elements using an algorithm that looks a lot like ElGamal encryption. To commit to $W \in \mathbb{G}_1$ it chooses random field elements $r,s$, sets $$ C = g_1^r g_2^s, \ D = W g_3^r g_4^s $$ and returns $(C,D)$. We have expressed the commitment with respect to $\mathbb{G}_1$. To commit to elements in $\mathbb{G}_2$ we use the same method with respect to the generators $(\widehat{h}_1\ldots \widehat{h}_4)$ instead of $(g_1\ldots g_4)$.

Typically when we present this commitment scheme to cryptographers their immediate response is "why two generators?" or "why not use Pedersen commitments?".  The answer to this question is highly nuanced and answering it here would disrupt the flow of this explanation. Thus we're not going to. But as a teaser, we will say that Groth and Sahai describe this commitment scheme as one that either satisfies hiding or binding depending on how the setup parameters are chosen.


Now, in our particular case of ElGamal encryption, we commit to our witness $(\widehat{W_1}, W_2, \widehat{W_3})$ once for all equations $E_1-E_4$:
$$
\begin{array}{l}
(\widehat{C}_1, \widehat{D}_1) \leftarrow (\widehat{h}_1^{r_1} \widehat{h}_2^{s_1}, \ \widehat{W}_1 \widehat{h}_3^{r_1} \widehat{h}_4^{s_1})\\
(C_2, D_2) \leftarrow (g_1^{r_2} g_2^{s_2}, \ W_2 g_3^{r_2} g_4^{s_2})\\
(\widehat{C}_3, \widehat{D}_3) \leftarrow (\widehat{h}_1^{r_3} \widehat{h}_2^{s_3}, \ \widehat{W_3} \widehat{h}_3^{r_3} \widehat{h}_4^{s_3})
\end{array}
$$ 

### The Prover and The Verifier
While the commitments $(\widehat{C}_1, \widehat{D}_1, C_2, D_2, \widehat{C}_3, \widehat{D}_3)$ are shared across all pairing product equations, each pairing equation requires a unique set of $8$ proof elements and $4$ verifier equations, so forms a "sub-proof". Here, mostly to stay concise, we show and later derive the proof system (prover and verifier) only for the second equation $E_2$. For the full system thus, prover must produce proofs for all four equations, and verifier must verify them all.


Recall that $E_2$ has the form
$$
    e(\mathsf{CT}_2, \widehat{h}_1)= e(\mathsf{pk}, \widehat{W}_1) e(W_2, \widehat{h}_1)  \tag{$E_2$}
$$
The honest prover needs to construct the following eight elements, where $\alpha,\beta,\gamma,\delta$ are sampled randomly:
$$
\begin{array}{l c l}
\Theta_1 = \mathsf{pk}^{r_1} g_3^{\alpha} g_4^{\beta} & & \widehat{\Phi}_1 = h_1^{r_2} h_3^{-\alpha} h_4^{-\gamma}\\
\Theta_2 = \mathsf{pk}^{s_1} g_3^\gamma g_4^{\delta} & & \widehat{\Phi}_2 = h_1^{s_2} h_3^{-\beta} h_4^{-\delta}\\
\Theta_3 = g_1^\alpha g_2^{\beta} & & \widehat{\Phi}_3 = h_1^{-\alpha} h_2^{-\gamma}\\
\Theta_4 = g_1^\gamma g_2^{\delta} & & \widehat{\Phi}_4= h_1^{-\beta} h_2^{-\delta}
\end{array}
$$ 
And the four equations $V_1 \ldots V_4$ the verifier must check on the commitments and proof elements are as follows:
$$
\begin{array}{l l r}
e(\Theta_1,\widehat{h}_3)e(\Theta_2,\widehat{h}_4)e(g_3,\widehat{\Phi}_1)e(g_4,\widehat{\Phi}_2) &= e(D_2 / \mathsf{CT}_2,\widehat{h}_1)e(\mathsf{pk},\widehat{D}_1) & \hspace{1cm} (V_1) \\
e(\Theta_1,\widehat{h}_1)e(\Theta_2,\widehat{h}_2)e(g_3,\widehat{\Phi}_3)e(g_4,\widehat{\Phi}_4) &= e(\mathsf{pk},\widehat{C}_1) & \hspace{1cm} (V_2) \\
e(\Theta_3,\widehat{h}_3)e(\Theta_4,\widehat{h}_4)e(g_1,\widehat{\Phi}_1)e(g_2,\widehat{\Phi}_2) &= e(C_2,\widehat{h}_1)  & \hspace{1cm} (V_3) \\
e(\Theta_3,\widehat{h}_1) e(\Theta_4,\widehat{h}_2) e(g_1,\widehat{\Phi}_3)e(g_2,\widehat{\Phi}_4) & = 1 & \hspace{1cm} (V_4)
\end{array}
$$ 
The reader is encouraged to attempt deriving the same equations for $E_1,E_3$ which are both easier than our case (we put our derivation for them at the end of the blog post). A more sadistical writer might also ask the reader to derive equations for $E_4$ as an exercise (possibly hinting that it is a simple), but after having attempted this exercise for ourselves we realised that $E_4$ is more involved due to its quadratic component.   Thus at the end of this document we will actively discuss $E_4$.

The form of proof elements and equations is somewhat homogeneous: we always have 8 proof elements and 4 verification equation per pairing equation, and the LHS of verification equations is always the same. However, the number of pairings in verification equations depends on the particular form of the pairing equation (reflected in the RHS). The commitments, as mentioned before, are generated once for all pairing equations, which amounts to 2 elements per witness element.

The following illustration shows how it works on a large scale:

<p align="center">
<img src="/images/posts/groth-sahai-explainer/figure-2.png" alt="Groth-Sahai Diagram" width="900"/>
</p>

## Deriving Equations for $E_2$
The intention of this section is to provide an intuitive step-by-step explanation of how the proof elements and verification equations for the pairing product equation $E_2$ are derived. We describe our general strategy, but after that things are going to get more technical. To readers that don't fancy wading through pages of algebra, we recommend you stop reading after the general strategy is explained. To other readers who are more dedicated to understanding the magic behind GS proofs, we recommend you get comfortable with continously switching between additive and multiplicative notation because we do this a lot (we promise not in the same equation).

### The General Strategy

We have a pairing product equation that the prover claims to hold for hidden witness variables. The prover cannot give the witness in the clear, this would violate zero-knowledge, but it still must tell the verifier *something* about its witness.  The prover therefore generates a commitment which binds them to their witness without revealing any additional information.

Our general strategy now is to find an alternative set of pairing product equations that hold if and only if the contents of the commitments satisfy the original pairing product equation. Our strategy will proceed in two parts.
* During our first part we search for intemediary proof elements that satisfy an intermediary set of pairing product equations if and only if the contents of the commitment satisfy the original pairing product equation. We treat soundness as if it holds unconditionally i.e. as if the only way for the prover to cancel out the randomness from the CRS is to multiply by zero. In the formal proof, we actually show that soundness does hold unconditionally provided the CRS is chosen carefully.
* During our second part, we show how to randomise the intemediary proofs and pairing product equations in a way that fully hides the witness. This results in our final equations. Here we focus mostly on satisfying zero-knowledge but we must not break soundness in the process.  In other words we try to ensure that a malicious verifier learns nothing from an honest prover, beyond the correctness of the ciphertext.

For arguing indistinguishability, one of the key properties  we require is that the number of randomisers is equal to the number of proof elements minus the number of verifier equations.  That way we can say e.g. that Element 1 is random, Element 2 is random, and Element 3 is the unique value satisfying Equation 1 given Elements 1 and  2. Thus our strategy is to add in additional randomisers to our proof elements and edit our verifier equations such that they still hold for the randomised proofs. To keep things sound we also have to add additional verifier equations to enforce that the prover doesn't abuse their newfound freedom. The other property we require is that there are no linear combinations between our randomisers such that they cancel out in undesirable ways. While deriving our equations for ($E_2$) we are merely going to optimistically hope that this holds, but formally check that it is the case later.


### The Intemediary Pairing Product Equations for Commitments

For the first part of our strategy, we must find an intermediary set of pairing product equations demonstrating that the contents $(\widehat{W}_1, W_2)$ of the commitments
$$
(\widehat{C}_1, \widehat{D}_1) = (\widehat{h}_1^{r_1} \widehat{h}_2^{s_1}, \widehat{W}_1 \widehat{h}_3^{r_1} \widehat{h}_4^{s_1}) \quad (C_2, D_2) = (g_1^{r_2} g_2^{s_2}, W_2 g_3^{r_2} g_4^{s_2}) 
$$ 
satisfy the second equation
$$
    e(\mathsf{CT}_2, \widehat{h}_1) e(\mathsf{pk}, \widehat{W}_1^{-1}) e(W_2^{-1}, \widehat{h}_1) = 1 \tag{$E_2$}
$$


For this explanation we find it helpful to work in logarithms, so here is some notation denoting the logarithms of generators in the CRS
$$
\begin{array}{c c c }
    g_2 = g_1^x\qquad&&\widehat{h}_2 = \widehat{h}_1^{\widehat{u}}\\
    g_3 = g_1^y\qquad&&\widehat{h}_3 =\widehat{h}_1^{\widehat{v}}\\
    g_4 = g_1^z\qquad&&\widehat{h}_4 =\widehat{h}_1^{\widehat{\ell}}
\end{array}
$$
Then the logarithms of our commitments are given by
$$
(\widehat{c}_1, \widehat{d}_1)  = (r_1 +\widehat{u} s_1 ,
\widehat{w}_1+ r_1 \widehat{v}+ s_1 \widehat{\ell})
\text{ and }
(c_2, d_2)  =
(r_2+xs_2,w_2+r_2 y+s_2 z)
$$

If we now actually look at the logarithmic equation defined by ($E_2$) we get that 
$$ 
\log_{g_1} \mathsf{CT}_2-\mathsf{sk}\cdot \widehat{w}_1=w_2 \tag{$L_2$} 
$$ 
where $\mathsf{sk} = \log_{g_1}(\mathsf{pk})$. Notice that $r_1,s_1, s_2, r_2$ are known to the prover while $x,y,z,\widehat{u}, \widehat{v},\widehat{\ell}$ are not. We make no assumptions on whether $\mathsf{sk}$ is known to the prover or not.

**Our derivation strategy** is, by introducing new variables, to obtain a set of equations equivalent to $L_2$ such that
* The equations do not contain $\widehat{w}_1,w_2$;
* The equations are bilinear, i.e. each term has at most one variable from each group.


*Step 1:* We first express $\widehat{w}_1$ and $w_2$ in terms of the commitments $(\widehat{c}_1, \widehat{d}_1, c_2, d_2)$ and the randomness $\widehat{r}_1$, $\widehat{s}_1, r_2, s_2$. The commitment $\widehat{D}_1$ should use the same randomness $\widehat{r}_1$, $\widehat{s}_1$ as the commitment $\widehat{C}_1$. Therefore, we substitute $r_1 = \widehat{c}_1 - \widehat{u} s_1$ into the equation for $\widehat{w}_1$ and obtain:
$$
\widehat{w}_1 = \widehat{d}_1 -  (\widehat{c}_1 - \widehat{u} s_1 ) \widehat{v} -  s_1 \widehat{\ell}
$$ 
Similarly for the second commitment: $$w_2 = d_2 -  (c_2 - x s_2) y -  s_2 z$$

*Step 2:* Substituting into $(L_2)$ we get
$$
\log{\widehat{\mathsf{CT}_2}} - \mathsf{sk} \cdot \Big( \widehat{d}_1 -  (\widehat{c}_1 - \widehat{u} s_1 ) \widehat{v} -  s_1 \widehat{\ell} \ \Big) = d_2 -  (c_2 - x s_2) y -  s_2 z
$$

*Step 3:* The terms $\log{\widehat{\mathsf{CT}}_2}, \mathsf{sk} \cdot \widehat{d}_1, d_2$ are already in the pairing equation form (degree at most two, at most two elements from different groups), so we leave them alone, moving to the RHS, and swapping sides of the equation: 
$$
\mathsf{sk} \cdot  \widehat{d}_1    - \log{\widehat{\mathsf{CT}}_2} +  d_2 =   \big(c_2 - x s_2\big) y +  s_2 z +  \mathsf{sk} \cdot \big(\widehat{c}_1 - \widehat{u} s_1 \big) \widehat{v} +  \mathsf{sk} \cdot s_1 \widehat{\ell} 
$$ 
Now, we want the RHS summands to be in the pairing-friendly form too. Currently they are not. For example, we cannot pair $C_2$ with $g_3 = g_1^y$ because these are both in the same source group.

*Step 4:* To get the RHS into a pairing friendly form, we will introduce new elements. For each summand we introduce one proof element. For example, where $y$ is multiplied by $(c_2 - x s_2)$, we introduce $\widehat{\phi}_1' = c_2 - s_2 x$. This suggests creating four additional elements:
$$
\begin{array}{ r c l l }
\theta_1'  & = &  \mathsf{sk} \cdot (\widehat{c}_1 - s_1 \widehat{u}) & \quad (= \mathsf{sk} \cdot r_1) \\
\theta_2'   & = &  \mathsf{sk}  \cdot s_1 & \\
\widehat{\phi}_1'  & = & c_2 - s_2 x  & \quad (= r_2)\\
\widehat{\phi}_2'  & = & s_2 &
\end{array}
$$ 
The additional proof elements we introduced is somewhat arbitrary --- there are many (closely related if not equivalent) ways to construct GS verification equations. Now our first equation is in the following well-formed pairing-compatible form:
$$
\mathsf{sk} \cdot \widehat{d}_1 + d_2 - \log{\mathsf{CT}_2}  =  \theta_1' \widehat{v} + y \widehat{\phi}_1' +  \theta_2' \widehat{\ell} + z \widehat{\phi}_2'
$$

*Step 5:* Our fifth and final step for determining the intemediary pairing equations is to enforce the previous four equations for $\Theta_1',\Theta_2',\widehat{\Phi}_1',\widehat{\Phi}_2'$. We start by joining the first two (substituting the second into the first) and obtaining: $$\theta_1' = \mathsf{sk} \cdot \widehat{c}_1 - \theta_2' \widehat{u}$$ Similarly, by joining the third and the fourth equations, we get:
$$
\widehat{\phi}_1' = c_2 - \widehat{\phi}_2' x
$$

*Resulting Intemediary Pairing Product Equation:* Putting all $5$ steps together, our intemediary pairing product equation challenges the prover to find
$$
\Theta_1' = \mathsf{pk}^{r_1}, \  \Theta_2' = \mathsf{pk}^{s_1}, \widehat{\Phi}_1' = \widehat{h}_1^{r_2}, \ \widehat{\Phi}_2' = \widehat{h}_1^{s_2}
$$ 
such that they satisfy
$$
\begin{array}{ rl r}
    e(\mathsf{pk}, \widehat{D}_1) e(D_2 \mathsf{CT}_2^{-1}, \widehat{h}_1) & = e(g_3, \widehat{\Phi}_1)e(g_4, \widehat{\Phi}_2) e(\Theta_1, \widehat{h}_3) e(\Theta_2, \widehat{h}_4) 
    & \hspace{1 cm } (V_1') \\
    e(\mathsf{pk}, \widehat{C}_1)  & = e(\Theta_1, \widehat{h}_1) e(\Theta_2, \widehat{h}_2)  
    & (V_2')  \\
    e(C_2, \widehat{h}_1) & = e(g_1, \widehat{\Phi}_1) e(g_2, \widehat{\Phi}_2) 
    & (V_3') 
\end{array}
$$  
(Proof elements in verification equations are without primes since they are considered to be formal variables.) Together these show that the commitments $(\widehat{C}_1, \widehat{D}_1)$ and $(C_2, D_2)$ contain witness elements $\widehat{W}_1$ and $W_2$ such that the second pairing product equation ($E_2$) is satisfied.

We are now going to frustrate the reader by observing that the above process was rather circular. Indeed we cannot reveal $\Theta_1', \Theta_2', \widehat{\Phi}_1', \widehat{\Phi}_2'$ in the clear:  they reveal too much information about the witness and violate zero-knowledge. For example observe that 
$$ 
e(D_2, \widehat{h}_1) e(g_3^{-1}, \widehat{\Phi}_1') e(g_4^{-1}, \widehat{\Phi}_2') = e(g_1^{m}, \widehat{h}_1) 
$$ 
for $m$ our secret message. The next step, however, will not be circular and we will show how to randomise these proof components in a manner that does not break zero-knowledge. That we have really gained is that $\Theta_1', \Theta_2', \widehat{\Phi}_1', \widehat{\Phi}_2'$ depend only on the original pairing product equations and the commitment randomness $r_1, s_1, r_2, s_2$. In particular they do not depend on the witness $\widehat{W}_1$, $W_2$.

A general property that is required (but not sufficient!) for zero knowledge is that *number of randomisers $\geq$ number of proof elements $-$ number of verification equations*. Here we have $4$ commitment elements with $4$ randomisers and then $4$ proof elements with no additional randomisers. Given $3$ verifier equations this leaves us $1$ randomiser short.


### Adding Zero-Knowledge:  Getting Sufficient Randomisers
For the second part of our strategy, we must randomise our intermediary proofs $(\Theta_1', \Theta_2', \widehat{\Phi}_1', \widehat{\Phi}_2')$ and pairing product equations $(V_1'), (V_2'), (V_3')$ to keep the witness hidden. We do this by adding blinding factors to $\Theta_1',\Theta_2'$ (order does not matter), and cancelling out the additional noise using other proof elements. Often the only way we can balance the randomised pairing equations is by adding additional proof elements. When we do this, we either add at least one new randomiser to the new proof element, or a new verifier equation which is a quadratic combinations of our other proof elements.

*Step 1:*  We first introduce a randomiser to $\Theta_1'$. We must then edit our intemediary equations to adjust for the extra randomness. We set 
$$ 
\theta_1'' =  \theta_1' + y \alpha 
$$
 By substituting this into the RHS of $(V_1')$ 
 $$
\widehat{\phi}_1' y + \widehat{\phi}_2' z + \theta_1  \widehat{v} +  \theta_2 \widehat{\ell} 
$$ 
we see that an additional term $y \alpha \widehat{v}$ has been acquired. This is unwanted noise that we must cancel out. To cancel the extra terms we edit $\widehat{\phi}_1'$ accordingly
$$
\widehat{\phi}_1'' =\widehat{\phi}_1' - \alpha \widehat{v}
$$ 
because this term is multiplied by $y$. Now $(\Theta_1'', \Theta_2', \Phi_1'', \Phi_2')$ satisfy $(V_1')$ and do not reveal the witness.


*Step 2:*  We edit $(V_2')$ so that our randomised proof elements can satisfy it. The RHS of $(V_2')$ is given by 
$$
\theta_1''  + \theta_2' \widehat{u}
$$
and this has aquired the additional noise $y \alpha$. We cannot hope to cancel this noise out with $\Theta_2$ because of the $\widehat{u}$ multiplier. For soundness, we also want to enforce that the noise added  in $\Theta_1''$ is actually a multiple of $y$ and does not interfere with  the witness. We thus introduce a new proof element that will be paired with $y$ blinded by an additional randomiser $\gamma$ 
$$
\widehat{\phi}_3 = - \alpha - \gamma \widehat{u}
$$ 
And therefore, $(V_2'')$ becomes
$$
    \mathsf{sk} \cdot \widehat{c}_1  = \theta_1'' + \theta_2' \widehat{u} + y \widehat{\phi}_3 \tag{$V_2''$}
$$
Now $\widehat{\phi}_3$ does not prevent $(V_2')$ from being satisfied whenever $(V_2'')$ is satisfied because $y$ is an unused basis. To make this equation balance we modify $\Theta_2'$ and get 
$$
\theta_2'' = \theta_2' + \gamma y
$$ 
and we see $(V_2'')$ is still satisfied.

*Step 3:*  We look back at $(V_1')$ with respect to our randomised proof element $\Theta_2''$. By substituting this into the RHS of $(V_1')$ 
$$
\widehat{\phi}_1'' y + \widehat{\phi}_2' z + \theta_1''  \widehat{v} +  \theta_2'' \widehat{\ell}
$$ 
we see that an additional term $\gamma y \widehat{\ell}$ has been acquired. This is unwanted noise that we must cancel out. To cancel the extra terms we edit $\widehat{\phi}_1''$ accordingly 
$$
\widehat{\phi}_1 =\widehat{\phi}_1' - \alpha \widehat{v}  - \gamma \widehat{\ell}
$$ 
because this term is multiplied by $y$. Now $(\Theta_{1}'', \Theta_2', \Phi_1, \Phi_2')$ satisfy $(V_1')$ and do not reveal the witness.

*Step 4:* We edit $(V_3')$ so that our randomised proof elements can satisfy it. The RHS of $(V_3')$ is given by
$$
    \widehat{\phi}_1 + x \widehat{\phi}_2'
$$ 
and this has aquired the additional noise $-\alpha \widehat{v} - \gamma \widehat{l}$. To cancel out the extra noise we introduce two new proof elements that will be paired with $\widehat{v}$ and $\widehat{l}$ respectively, and blind them with $\beta$ and $\delta$ 
$$
\theta_3 = \alpha + x \beta  \qquad \qquad \theta_4 = \gamma + x \delta 
$$ 
And therefore, $(V_3')$ becomes
$$
    \widehat{c}_2  = \theta_3\widehat{v} + \theta_4 \widehat{\ell} + \widehat{\phi}_1  + x \widehat{\phi}_2'  \tag{$V_3$}
$$
Now $\Theta_3, \Theta_4$ does not prevent $(V_3')$ from being satisfied whenever $(V_3)$ is satisfied because $\widehat{v}, \widehat{\ell}$ is an unused basis. To make this equation balance we modify $\widehat{\phi}_2$: 
$$
\widehat{\phi}_2 =\widehat{\phi}_2'  - \beta \widehat{v}   - \delta \widehat{\ell} 
$$ 
and we see $(V_3)$ is still satisfied.

*Step 5:* We look back at $(V_1')$ with respect to our randomised proof element $\widehat{\phi}_2$. By substituting this into the RHS of $(V_1')$ 
$$
\widehat{\phi}_1 y + \widehat{\phi}_2 z + \theta_1''  \widehat{v} +  \theta_2'' \widehat{\ell}
$$ 
we see that an additional term $- \beta z \widehat{v}   - \delta z \widehat{\ell}$ has been acquired. This is unwanted noise that we must cancel out. To cancel the extra terms we edit $\Theta_1''$ and $\Theta_2''$ accordingly
$$
\begin{array}{c}
    \theta_1 = \theta_1''  + \beta z =  \theta_1' +  \alpha y + \beta z \\
    \theta_2 = \theta_2''  + \delta z =  \theta_2' + \gamma y + \delta z \\
\end{array}
$$ 
Now $(\Theta_{1}, \Theta_2, \Phi_1, \Phi_2)$ satisfy $(V_1')$ and do not reveal the witness.


*Step 6:*  We edit $(V_2'')$ so that our randomised proof elements can satisfy it. The RHS of $(V_2'')$ is given by $$\theta_1 + \theta_2 \widehat{u} + y \widehat{\phi}_3$$ and this has aquired the additional noise $\beta z + \delta z \widehat{u}$.

We shall need to add a proof element which is paired with $z$ to cancel the noise. We cannot balance any additional randomness that this new element introduces because $\Theta_1$ and $\Theta_2$ already both have $z$ components. Thus for our final proof element to not use up a randomiser we instead add a verification equation. See that
$$
\beta z + \delta z \widehat{u} =   \frac{z}{x} (  \theta_3 + \theta_4 \widehat{u} + \widehat{\phi}_3)
$$ 
We thus introduce a new proof element 
$$
\widehat{\phi}_4 = - \beta  - \delta \widehat{u}
$$ 
and a verification equation
$$
    0  = \theta_3 + \theta_4 \widehat{u} + \widehat{\phi}_3  + x \widehat{\phi}_4  \tag{$V_4$}
$$

Now $(V_2'')$ becomes
$$
    \mathsf{sk} \cdot \widehat{c}_1  = \theta_1 + \theta_2 \widehat{u} + y \widehat{\phi}_3 + z \widehat{\phi}_4 \tag{$V_2$}
$$
We do not need to edit $(V_1')$ or $(V_3)$ because no proof elements have been edited.

*Resulting Verifier Equations:* Putting everything together, we have the following eight proof elements
$$
\begin{array}{l l c l}
& \Theta_1 = \mathsf{pk}^{r_1} g_3^{\alpha} g_4^{\beta} \quad && \widehat{\Phi}_1 = h_1^{r_2} h_3^{\alpha} h_4^{\gamma}\\
& \Theta_2 = \mathsf{pk}^{s_1} g_3^\gamma g_4^{\delta} && \widehat{\Phi}_2 = h_1^{s_2} h_3^{\beta} h_4^{\delta}\\
& \Theta_3 = g_1^\alpha g_2^{\beta} &&\widehat{\Phi}_3 = h_1^{-\alpha} h_2^{-\gamma}\\
& \Theta_4 = g_1^\gamma g_2^{\delta} &&\widehat{\Phi}_4= h_1^{-\beta} h_2^{-\delta}
\end{array}
$$
and $4$ verification equations
$$
\begin{array}{r c r}
    e(\mathsf{pk}, \widehat{D}_1) e(D_2 \cdot \mathsf{CT}_2^{-1}, \widehat{h}_1) & = e(g_3, \widehat{\Phi}_1)e(g_4, \widehat{\Phi}_2) e(\Theta_1, \widehat{h}_3) e(\Theta_2, \widehat{h}_4)   
    &
    \hspace{1cm} (V_1)
    \\
    e(\mathsf{pk}, \widehat{C}_1)  & = e(\Theta_1, \widehat{h}_1) e(\Theta_2, \widehat{h}_2)e(g_3, \widehat{\Phi}_3) e(g_4, \widehat{\Phi}_4)  
    & (V_2)
    \\
    e(C_2, \widehat{h}_1) & = e(\Theta_3, \widehat{h}_3) e(\Theta_4, \widehat{h}_4) e(g_1, \widehat{\Phi}_1) e(g_2, \widehat{\Phi}_2)  
    & (V_3)
    \\
    1 & = e(\Theta_3, \widehat{h}_1) e(\Theta_4, \widehat{h}_2) e(g_1, \widehat{\Phi}_3) e(g_2, \widehat{\Phi}_4) & (V_4)
\end{array}
$$
The verification equations $(V_1), (V_2), (V_3), (V_4)$ given in Section 3 are exactly equal to what we have just derived.


This completes our explanation for how the prover and verifier for $(E_2)$ are derived.  In the next sections we will dive into the security rationale behind this construction, and give more formal arguments of security than simply stating that we have the correct number of randomisers. Still, if you are constructing a zero-knowledge proof but have less randomisers than proof elements minus verifier equations, then it is time to become very suspicious of your result.


## Proving Security
The previous section explains how, intuitively, one should arrive at GS equations, using $E_2$ as an example input equation. Now we explain (and formally prove) why the resulting system of equations satisfies completeness, soundness, and zero-knowledge.

### Completeness
*(Does anyone ever actually prove completeness? The proofs satisfy the verifier in our implementation...)*

<img src="/images/posts/groth-sahai-explainer/code-completeness.png" alt="Completeness, as illustrated by our implementation" width="600"/>

Completeness of the proof system means that every honestly-generated proof verifies with probability one. That is, if $W_1,W_2,W_3$ satisfy $E_2$, then $\vec\Pi = (\vec\Theta,\vec\Phi)$ satisfies $V_1 \land V_2 \land V_3 \land V_4$. It can be easily seen that this holds by construction because proof elements that satisfy the original equations (commitment validity + $(E_2)$) must also satisfy the derived equations.

### Soundness

Soundness of the non-interactive proof system means that for any adversarially constructed proof that verifies there exists a witness to the given relation (in our case, the witness is ($\widehat{W}_1, W_2$)). The GS proof that we presented, like with most of the common zero-knowledge proofs today, is computationally sound assuming that a cryptographic problem is hard. The assumption here is the SXDH (Symmetric External Diffie-Hellman): nobody can tell the difference between random $(g_1,g_2,g_3,g_4)$ and $(g_1,g_1^x,g_1^y,g_1^{xy})$ in $\mathbb{G}_1$ and analogously for $\mathbb{G}_2$. Looking ahead, this will help us argue that a commitment setup $\left ( (g_1,g_1^x,g_1^y,g_1^{xy}),(\widehat{h}_1,\widehat{h}_1^{\widehat{u}},\widehat{h}_1^{\widehat{v}},\widehat{h}_1^{\widehat{u} \widehat{v} }) \right )$ looks similar to $\left ( (g_1,g_2,g_3,g_4),(\widehat{h}_1,\widehat{h}_2,\widehat{h}_3,\widehat{h}_4) \right )$.

The *intuition* about soundness can be found in the way the equations $V_1 \ldots V_4$ were constructed. We built them such that when the original $E_2$ holds for some witness elements, the final $\{V_i\}_i$ hold too ($E_2 \Rightarrow \{V_1 \ldots V_4\}$). But the transformations that we applied to our equations are in fact one-to-one, and it is also true that when $\{V_i\}_i$ hold, $E_2$ holds for some witness ($\{V_1 \ldots V_4\} \Rightarrow E_2$).

<img src="/images/posts/groth-sahai-explainer/figure-5.png" alt="Soundness Illustration" width="700">

To formally demonstrate soundness, the only cryptographically elaborate detail is to show that $(\widehat{C}_1,\widehat{D}_1), (C_2, D_2)$ are always commitments that contain some $\widehat{W}_1, W_2$ and not some stray elements. This is where SXDH comes in play. The reader can follow a more formal assertion of soundness in the hidden section next.

<details>

<summary>Collapsible: Commitment scheme under standard and SXDH setups.</summary>

The commitment scheme with the standard setup, where all base elements are randomly picked, is perfectly hiding and computationally binding. Because of this, when we see a commitment under standard setup, intuitively, we cannot claim that anything is "contained" inside of it, which is necessary for the existentially qualified soundness statement: "for every verifying proof there *exists* a witness". We only know that for whatever was put in there, it's computationally impossible for the prover to find another element that this commitment opens to. Put more explicitely, upon seeing a *commitment* $(\widehat{C}_1, \widehat{D}_1)$ we cannot extract some unique $\widehat{W}_1$ such that the commitment contains $(\widehat{h}_1^{r_1} \widehat{h}_2^{s_1}, \widehat{W}_1 \widehat{h}_3^{r_1} \widehat{h}_4^{s_1})$ because there are multiple solutions.

When instantiated with the SXDH setup though $(g_1,g_1^x,g_1^y,g_1^{xy}),(\widehat{h}_1,\widehat{h}_1^{\widehat{u}},\widehat{h}_1^{\widehat{v}},\widehat{h}_1^{\widehat{u} \widehat{v}})$, the commitment scheme becomes, in contrast, computationally hiding and perfectly binding. Comparing to the previous situation, we know that for every commitment, there is exactly one valid element committed that can lead to this outcome (one-to-one correspondence). This is just as an encryption scheme (actually it is literally ElGamal encryption). This means that we, knowing the alternative setup trapdoors $(x,y, \widehat{u}, \widehat{v})$, can decrypt the commitments and obtain the witness.

<img src="/images/posts/groth-sahai-explainer/figure-3.png" alt="Honest vs subverted setup, hiding vs binding" width="600"/>

Our *strategy for proving soundness* is therefore to show that we can extract a witness that satisfies $E_2$ from *any* proof that is valid for the SXDH (=subverted) setup. One extracts a witness by decrypting the commitments (see step 1 below), and shows it is a witness by checking $V_1$-$V_4$ equations (step 2 below). The strategy proves the soundness for not only SXDH setups but for any setups that are indistinguishable from such. The SXDH assumption tells us that any random setup should be as such, and thus we prove the soundness. Now back to the witness:

* First of all, each pair of elements $(C_2,D_2) \in \mathbb{G}_1 \times \mathbb{G}_1$ is a proper perfectly binding commitment. It is easy to see that with $c_2 = r_2 + x s_2$ we have $d_2 = w_2 + y r_2 + x y s_2 = w_2 + y c_2$. This means that in honestly constructed commitments under SXDH the second element is always deterministically defined by the first. As argued for any $(C_2,D_2)$ there always exist $w_2$ such that $(C_2,D_2) = \mathsf{Commit}(g_1^{w_2},(r_2,s_2)) = (g_1^{r_2 + x s_1}, g_1^{w_2} g_1^{y (r_2 + x s_2 ) })$ for some $r_2,s_2$.
Similarly, $(\widehat{C}_1,\widehat{D}_1) = \mathsf{Commit}(h_1^{\widehat{w}_1},(r_1,s_1)) = (\widehat{h}_1^{r_1 + \widehat{u} s_1}, \widehat{h}_1^{\widehat{w}_1} \widehat{h}_1^{\widehat{v} (r_1 + \widehat{u} s_1 )})$.

* Now we review $V_1 \ldots V_4$ in logarithms with commitment representations given:
$$
\begin{array}{cl}
\theta_1\widehat{v} + \theta_2\widehat{u}\widehat{v} + y\widehat{\phi}_1 + xy \widehat{\phi}_2 &= \underbrace{w_2 + y c_2}_{d_2} - \log{\mathsf{CT}_2} + \mathsf{sk} \underbrace{(\widehat{w}_1 + \widehat{v} \widehat{c}_1)}_{\widehat{d}_1}\\
\theta_1 + \theta_2\widehat{u} + y\widehat{\phi}_3 + xy \widehat{\phi}_4 &= \mathsf{sk} \cdot \widehat{c}_1\\
\theta_3\widehat{v} + \theta_4\widehat{u}\widehat{v} + \widehat{\phi}_1 + x \widehat{\phi}_2 &= c_2\\
\theta_3 + \widehat{u} \theta_4 +  \widehat{\phi}_3+ x\widehat{\phi}_4   &= 0
\end{array} 
$$
Performing arithmetic operations on both sides of each equation simultaneously, $V_1 - V_2 \cdot \widehat{v} - V_3 \cdot y$ is equal to:
$$
-\widehat{v}(y \widehat{\phi}_3 + xy \widehat{\phi}_4) - y(\theta_3 \widehat{v} + \theta_4 \widehat{u} \widehat{v}) = w_2 + \mathsf{sk} \cdot \widehat{w}_1 - \log{\mathsf{CT}_2}
$$ 
LHS of which is exactly $\widehat{v} y V_4$, and since $V_4 = 0$, the left hand side is 0. So in the end we obtain, on the RHS, $w_2 + \mathsf{sk} \cdot \widehat{w}_1 - \log{\mathsf{CT}_2} = 0$ as expected from $E_2$.

</details>

### Zero-Knowledge


The GS system we constructed is computationally zero-knowledge. Intuitively, it is because commitments are sufficiently hiding, and proof elements are sufficiently randomized. To formally show computational ZK of our system we will (1) provide a simulator that works under a specific alternative CRS setup, (2) show that simulated proofs are indistinguishable from honest ones.

The trick with the simulation is the following one. First, the simulator uses an alternative setup for $\mathbb{G}_2$: $\widehat{h}_1$ random, $\widehat{h}_2 = \widehat{h}_1^{\widehat{u}}, \widehat{h}_3 = \widehat{h}_1^{\widehat{v}-1}, \widehat{h}_4 = \widehat{h}_1^{\widehat{u}\widehat{v}}$. Similarly in $\mathbb{G}_1$, $g_1$ is random, $g_2 = g_1^x$, $g_3 = g_1^{y-1}$ and $g_4 = g_1^{xy}$. Such a setup is indistinguishable from the honest one under SXDH.

Second, instead of committing to the witness values, the simulator commits to $1 \in \mathbb{G}_1,\mathbb{G}_2$ in both commitments (e.g. $D_2 = g_3^{r_2} g_4^{s_2}$). Then, the proof elements are kept almost the same, except that now the witness value can't enter $V_1$ from the commitment, so we must cancel $\mathsf{CT}_2$ there differently. We solve this by modifying $\Theta_1,\Theta_2$ such that the change only affects $V_1$, but not $V_2$ (these are the only equations in which $\Theta_1,\Theta_2$ are used).
$$
\begin{array}{l c l }
\Theta_1 = \mathsf{pk}^{r_1} g_3^{\alpha} g_4^{\beta} \cdot \mathsf{CT}_2^{-1} && \widehat{\Phi}_1 = h_1^{r_2} h_3^{-\alpha} h_4^{-\gamma}\\
\Theta_2 = \mathsf{pk}^{s_1} g_3^\gamma g_4^{\delta} \cdot \mathsf{CT}_2^{1/u} && \widehat{\Phi}_2 = h_1^{s_2} h_3^{-\beta} h_4^{-\delta}\\
\Theta_3 = g_1^\alpha g_2^{\beta} &&\widehat{\Phi}_3 = h_1^{-\alpha} h_2^{-\gamma}\\
\Theta_4 = g_1^\gamma g_2^{\delta} &&\widehat{\Phi}_4= h_1^{-\beta} h_2^{-\delta}
\end{array} 
$$
Looking at $V_1$, the extra elements in $\Theta_1,\Theta_2$ will produce exactly $\mathsf{CT}_2$: $-\log{\mathsf{CT}_2} (\widehat{v}-1) + \frac{\log{\mathsf{CT}_2}}{\widehat{u}} \widehat{u} \widehat{v} = \log{\mathsf{CT}_2}$.  At the same time, in $V_2$ these extra elements will cancel each other: $-\log{\mathsf{CT}_2} + \frac{\log{\mathsf{CT}_2}}{\widehat{u}} \widehat{u} = 0$.

So this simulator produces the right result without using witness at all, at the expense of having access to the CRS trapdoor, while in the honest case the prover must know the witness by soundness (and of course doesn't know the CRS trapdoor).

The next, more involved step, is to show formally is that the distribution of the simulated proof is the same as the distribution of the honest proof --- "fake proofs are good at being fake". Intuitively it holds because there are enough random variables, and the elements in which the simulator "cheats" are still distributed uniformly. Formally, we prove it in the collapsible section.

<details>
<summary>Collapsible: The Elaborate Proof of Zero Knowlegde</summary>

  Formally, composable zero-knowledge definition consists of two parts (See Definition 5 in the Groth-Sahai paper). First is the setup indistinguishability: adversary needs to decide between either honest CRS or an alternative one used by the simulator. Second is simulator indistinguishability: the setup in both distributions is subverted, but in one game adversary queries honest proofs, and in another one --- simulated ones.

  The first step, setup indistinguishability, is easy to show under SXDH. If an adversary $\mathcal{A}$ can tell the difference between honest and simulated setups, we can build a reduction $\mathcal{B}$, in which we merely pass the SXDH challenge $(\widehat{h}_1,\widehat{h}_2,\widehat{h}_3,\widehat{h}_4)$ to $\mathcal{A}$ as CRS of the form $(\widehat{h}_1,\widehat{h}_2,\widehat{h}_3/\widehat{h}_1,\widehat{h}_4)$. Obviously, $\mathcal{B}$ breaks SXDH then.

  Assume the second part of the definition, proof indistinguishability, and thus assume *alternative* setup (SXDH) in both real and simulated worlds from now on. We now only need to show that for every instance-witness pair, the distributions of honest proofs $\vec\Pi = (\vec\Theta,\vec\Phi)$ and simulated proofs $\vec\Pi'$ are perfectly indistinguishable. To start with, both $\vec\Pi$ and $\vec\Pi'$ contain exactly the same number of group elements; one can think of these two random variables as tuples of length 12 (containing 4 commitment elements, and 8 proof elements). Moreover, since we assume proofs from both $\vec\Pi$ and $\vec\Pi'$ verify, the verification equations $\{V_i\}$ restrict elements of these tuples. We will argue that both proof distributions can be viewed as consisting of a set of uniform tuple elements (subset of all proof elements), and other elements being defined from the first set by $\{V_i\}$.

  Think of $\{V_i\}_i$ as of polynomials, where variables are elements of $\vec\Pi$ and $\vec\Pi'$ (commitments and proof elements). First, fix $\widehat{C}_1,\widehat{D}_1,C_2,D_2$ (the choice is almost arbitrary). It can be easily seen that if we also fix $\Theta_1,\Theta_2,\widehat{\Phi}_1$ in the equation $V_1$ the only free variable that is left is $\widehat{\Phi}_2$. This means that $\widehat{\Phi}_2 = F_1(D_1,D_2,\Theta_1,\Theta_2,\widehat{\Phi}_1)$ for $W_1$ associated with $V_1$ that expresses $\widehat{\Phi}_2$ using other elements.

  Concretely, $V_1$ in our setup is: 
  $$
  \theta_1(\widehat{v}-1) + \theta_2\widehat{u}\widehat{v} + (y-1)\widehat{\phi}_1 + xy \widehat{\phi}_2 = d_2 - \log{\mathsf{CT}_2} + \mathsf{sk}\cdot \widehat{d}_1
  $$ 
  And thus 
  $$
   \widehat{\phi}_2 = \log\left(F_1(\widehat{D}_1,D_2,\Theta_1,\Theta_2,\widehat{\phi}_1)\right) := \frac{d_2 - \log{\mathsf{CT}_2} + \mathsf{sk}\cdot \widehat{d}_1 - \theta_1(\widehat{v}-1) - \theta_2\widehat{u}\widehat{v} - (y-1)\widehat{\phi}_1}{xy}
   $$

  Next, additionally from $\widehat{\phi}_3$ and $C_1$ the equation $V_2$ fixes $\widehat{\Phi}_4$, so from $V_2$: $$\theta_1 + \theta_2\widehat{u} + (y-1)\widehat{\phi}_3 + xy \widehat{\phi}_4 = \mathsf{sk}\cdot \widehat{c}_1$$ We get:
  $$
  \widehat{\phi}_4 = \log\left(F_2(\widehat{C}_1,\Theta_1,\Theta_2,\widehat{\Phi}_3)\right) := \frac{\mathsf{sk}\cdot \widehat{c}_1 - \theta_1 - \theta_2\widehat{u} - y\widehat{\phi}_3}{xy}
  $$

  Next, given a fixed $C_1$ we now have two equations $V_3$ and $V_4$ over two free variables $\Theta_3, \Theta_4$, so these two proof elements are also defined deterministically. Consider $V_3,V_4$:
  $$
  \begin{array}{ c l }
    \theta_3(\widehat{v}-1) + \theta_4\widehat{u}\widehat{v} + \widehat{\phi}_1 + x \widehat{\phi}_2 &= c_2\\
    \theta_3 + \widehat{u} \theta_4 +  \widehat{\phi}_3+ x\widehat{\phi}_4  &= 0
 \end{array}
 $$
 Now we obtain first by computing $V_4 \widehat{v} - V_3$: 
 $$
 \theta_3 + \widehat{v}(\widehat{\phi}_3 + x\widehat{\phi}_4) - \widehat{\phi}_1 - x \widehat{\phi}_2 + c_2 = 0
 $$ 
 From which:
 $$
 \begin{array}{ c l }
    \theta_3 = \log\left(F_3(C_2,\widehat{\phi}_1,\widehat{\phi}_2,\widehat{\phi}_3,\widehat{\phi}_4)\right) &:= \widehat{\phi}_1 + x \widehat{\phi}_2 -  \widehat{v}(\widehat{\phi}_3 + x\widehat{\phi}_4) - c_2\\
    \theta_4 = \log\left(F_4(\Theta_3,\widehat{\phi}_3,\widehat{\phi}_4)\right) &:= -\frac{ \theta_3 +  \widehat{\phi}_3 + x\widehat{\phi}_4 }{ \widehat{u} }
  \end{array}
 $$


  Therefore, we can say, that both proof distributions $\vec\Pi,\vec\Pi'$ have form:
 $$
 \begin{array}{  l }
     \big(\widehat{C}_1,\widehat{D}_1,C_2,D_2,\Theta_1,\Theta_2,\widehat{\Phi}_1,\widehat{\Phi}_3, \\
     \qquad \underbrace{F_1(\widehat{D}_1,D_2,\Theta_1,\Theta_2,\widehat{\Phi}_1)}_{\widehat{\Phi}_2}, \underbrace{F_2(\widehat{C}_1,\Theta_1,\Theta_2,\widehat{\Phi}_3)}_{\widehat{\Phi}_4}\\
     \qquad \underbrace{F_3(C_2,\widehat{\Phi}_1,F_1(\ldots),\widehat{\Phi}_3,F_2(\ldots))}_{\Theta_3}, \underbrace{F_4(\Theta_3,\widehat{\Phi}_3,F_2(\ldots))}_{\Theta_4}\big)
  \end{array}
 $$
  Where $F_1$ and $F_2$ in $F_3$ and $F_4$ substitute $\widehat{\Phi}_2$ and $\widehat{\Phi}_4$ correspondingly.

  So far we do not know the distribution of the first eight elements $\vec\Xi = \left(\widehat{C}_1,\widehat{D}_1,\ldots,\widehat{\Phi}_3\right)$. We will now argue that in both worlds elements of $\vec\Xi$ are distributed independently uniformly at random. This essentially concludes the proof, showing that in both worlds the distribution is exactly the same: 
  $$
  \vec\Pi = \vec\Pi' = (U_1,\ldots,U_8,F_1(U_2,U_4,U_5,U_6,U_7),F_2(\ldots), F_3(\ldots), F_4(\ldots))
  $$

  The independence and uniformity of elements in $\vec\Xi$ is simple to see from the following table:
  | $\vec\Xi$ | Real | Real log | Sim | Sim log |
  | --- | --- | --- | --- | --- |
  | $\widehat{D}_1$ | $\widehat{W}_1 \widehat{h}_3^{r_1} \widehat{h}_4^{s_1}$ | $\widehat{w}_1 + (\widehat{v}-1) r_1 + \widehat{u} \widehat{v} s_1$ | $\widehat{h}_3^{r_1} \widehat{h}_4^{s_1}$ | $(\widehat{v}-1) r_1 + \widehat{u} \widehat{v} s_1$ |
  | $D_2$ | $W_2 g_3^{r_2} g_4^{s_2}$ | $w_2 + (y-1) r_2 + xy s_2$ | $g_3^{r_2} g_4^{s_2}$ | $(y-1) r_2 + xy s_2$ |
  | $\Theta_1$ | $\mathsf{pk}^{r_1} g_3^{\alpha} g_4^{\beta}$ | $\mathsf{sk} \cdot r_1 + (y-1) \alpha + xy \beta$ | $\mathsf{pk}^{r_1} g_3^{\alpha} g_4^{\beta} \cdot \mathsf{CT}_2^{-1}$  | $\ldots - \log{\mathsf{CT}_2}$  |
  | $\Theta_2$ | $\mathsf{pk}^{s_1} g_3^\gamma g_4^{\delta}$ | $\mathsf{sk} \cdot s_1 + (y-1) \gamma + xy \delta$ | $\mathsf{pk}^{s_1} g_3^\gamma g_4^{\delta} \cdot \mathsf{CT}_2^{1/u}$ | $\ldots + \log{\mathsf{CT}_2} / u$  |
  | $\widehat{\Phi}_1$ | $h_1^{r_2} h_3^{-\alpha} h_4^{-\gamma}$ | $r_2 - (\widehat{v}-1) \alpha - \widehat{u} \widehat{v} \gamma$ | same | same  |
  | $\widehat{\Phi}_3$ | $h_1^{-\alpha} h_2^{-\gamma}$ | $- \alpha - \widehat{u} \gamma$ | same | same |
  | $\widehat{C}_1$ | $\widehat{h}_1^{r_1} \widehat{h}_2^{s_1}$ | $r_1 + \widehat{u} s_1$ | same | same |
  | $C_2$ | $g_1^{r_2} g_2^{s_2}$ | $r_2 + x s_2$ | same | same |

  Let's take a step back and recall how uniform distributions work, and in particular combine with each other. Intuitively, random variables are independent if none of them can be expressed as a deterministic function of others. Assuming $A,B$ are independently uniform over some $\mathbb{F}_p$, $A$ is independent from $A+B$ also, but $A,B,A+B$ are not mutually independent, since $A+B = F(A,B)$, where $F$ is summing its two arguments. Similarly, $A$ and $5*A$ are not independent, and neither are $A$ and $5 + A$. As a more complex example, if $A,B,C,D$ are independent, so are $X=A+B$, $Y=B+C$, $Z=C+D$. But then $X-Y+Z = A+B-B-C+C+D = A+D$, so $D+A$ is not independent from $X,Y,Z$.

  We start from the real world. Formally, to prove that the $\vec\Xi$ are linearly independent, we can consider them as 9-dimensional vectors, corresponding to 8 random variables $T := (s_1,r_1,s_2,r_2,\alpha,\beta,\gamma,\delta)$, and 1 constant. See the "real log" column in the last table, with values considered to be polynomials over $\gamma$. For such a set of vectors to be linearly independent, at least one $8\times 8$ submatrix (there are 9 of them) should have nonzero determinant. So we drop the constant row, and compute the determinant of the main 8 columns corresponding to $T$, which is equal to $x^3 y^2 u^2 (2v -1)$ (see the computation [here](https://www.wolframalpha.com/input/?i=det\%28\%7B\%7Bu\%2C0\%2Cuv\%2C0\%2C0\%2C0\%2C0\%2C0\%7D\%2C\%7B1\%2C0\%2Cv-1\%2C0\%2Cs\%2C0\%2C0\%2C0\%7D\%2C\%7B0\%2Cx\%2C0\%2Cxy\%2C0\%2C0\%2C0\%2C0\%7D\%2C\%7B0\%2C1\%2C0\%2Cy-1\%2C0\%2C0\%2C1\%2C0\%7D\%2C\%7B0\%2C0\%2C0\%2C0\%2Cy-1\%2C0\%2Cv-1\%2C-1\%7D\%2C\%7B0\%2C0\%2C0\%2C0\%2Cxy\%2C0\%2C0\%2C0\%7D\%2C\%7B0\%2C0\%2C0\%2C0\%2C0\%2Cy-1\%2Cuv\%2Cu\%7D\%2C\%7B0\%2C0\%2C0\%2C0\%2C0\%2Cxy\%2C0\%2C0\%7D\%7D\%29)). It is clear that when the setup is random, the probability of such a determinant to be zero is negligible, since we should guess at least one of the $x,y,u,v$ elements to have a particular value, the probability is $< 4/p$. This shows that $\vec\Xi$ are linearly independent as functions of $T$. Given that $\vec\Xi$ are themselves linear functions of $T$, they are independent as random variables. And since it is easy to see that each $\vec\Xi$ can be associated with a unique $T$, we conclude that in the real world $\vec\Xi$ are independently uniform.

  Now, as for the simulated world, take a look at the "Sim" and "Sim log" columns in the last table. It is easy to see that the last four elements $\widehat{\Phi}_1, \widehat{\Phi}_3,\widehat{C}_1,C_2$ are constructed exactly the same as in the real world.   As for the first four elements, we note that the same reasoning applies to them as in the real world: (1) these elements use exactly the same randomizers, so still we can assign a unique $\Phi$ element to each of those; (2) linear independence still holds, as we only add and remove constants from these four elements, therefore the matrix we consider is the same.

  Thus $\vec\Xi$ is distributed uniformly in both worlds, and thus $\vec\Pi$ and $\vec\Pi'$ are distributed equally in both worlds, and therefore the construction is zero-knowledge.


  Note that we in fact need to prove zero-knowledge for the full GS proof system built for *all* $E_i$ equations, and not just for $E_2$. Therefore, in a similar vein, we must provide a simulator for the whole system, and prove that proofs follow the same distribution in both worlds. To simulate the whole proof, we would first subvert a setup, and then run the sub-simulators for each equation separately. A careful reader could have noticed that the alternative setup for $\mathbb{G}_1$ could stay the same just for our case of $E_2$ (that is we don't use the fact $g_3 = g_1^{y-1}$) --- but exactly because we need to simulate in other equations, we need to subvert in both groups. Making the proof distribution indistinguishability statement for all $\{E_i\}$ simultaneously is also in fact similar to "concatenating" such statements for each $E_i$.   The commitments are reused across different verification equations, but they are distributed similarly in both worlds, and thus the proof elements that depend on them do too.

</details>


## Bonus: Deriving Proof Structure for $E_4$


In this section we explain how to derive the form of proof elements and verification equations for $E_4$, which we remind has the following form: 
$$
e(W_2, \widehat{W}_3)= e(W_2, \widehat{h}_1)  \tag{$E_4$}
$$ 
Although the general strategy is the same as for $E_2$, this case is a bit more complicated because $E_4$, unlike $E_2$, includes a product of two witness elements. In particular, in a few places where element grouping can be done in multiple ways, we will let the generic form of GS verification equations (e.g. like in $V_1 \ldots V_4$) guide our reasoning.


Recall that $(C_2,D_2)$ is a commitment to $w_2$ and $(\widehat{C}_3,\widehat{D}_3)$ commits to $\widehat{w}_3$. The equation $E_4$ we target is written in logarithms as $w_2 (\widehat{w}_3 - 1) = 0$. Expand the witnesses in it using equations for $d_2$ and $\widehat{d}_3$:
$$
(d_2 - r_2 y - s_2 z) (\widehat{d}_3 - r_3 \widehat{v} - s_3 \widehat{l} - 1) = 0
$$

In this equation, separate constant terms and terms that depend on $D_i$ only, because we can check them publicly.
$$
d_2 (\widehat{d}_3 - 1) = (r_2 y + s_2 z) (\widehat{d}_3 - 1) + d_2 (r_3 \widehat{v} + s_3 \widehat{l}) - (r_2 y + s_2 z) (r_3 \widehat{v} + s_3 \widehat{l})
$$

Next step would be to attempt to split the terms on the right hand side into several proof elements. But not any arrangement will work, and therefore we will use the "general form of the proof", trying to mimic $V_1 \ldots V_4$ for $E_2$. With this in mind, our task is to find $\Theta_1,\Theta_2,\widehat{\Phi}_1,\widehat{\Phi}_2$ such that:
$$
\theta_1 \widehat{u} + \theta_2 \widehat{l} + \widehat{\phi}_1 y + \widehat{\phi}_2 z = d_2 (\widehat{d}_3 - 1) \tag{$E_4.V_1$}
$$

But even with this restriction there exist many ways in defining what proof elements are. Here is how to get the working partition. Leave $(r_2 y + s_2 z) (\widehat{d}_3 - 1)$ as it is, and define
$$
\begin{array}{c}
  \widehat{\phi}_1 = r_2 (\widehat{d}_3 - 1)\\
  \widehat{\phi}_2 = s_2 (\widehat{d}_3 - 1)
\end{array}
$$
All the other terms do not depend in fact on $y$ or $z$! Here is why:
$$
\begin{array}{rl}
    d_2 (r_3 \widehat{v} + s_3 \widehat{l}) &- (r_2 y + s_2 z) (r_3 \widehat{v} + s_3 \widehat{l}) \\
    &= (d_2 - (r_2 y + s_2 z)) (r_3 \widehat{v} + s_3 \widehat{l}) \\
    &= (r_2 y + s_2 z + w_2 - (r_2 y + s_2 z)) (r_3 \widehat{v} + s_3 \widehat{l}) \\
    &= w_2 (r_3 \widehat{v} + s_3 \widehat{l})
\end{array}
$$
Therefore, define
$$
\begin{array}{c}
  \theta_1 = r_3 w_2 \\
  \theta_2 = s_3 w_2
\end{array}
$$

It is easy to check that these $\Theta_1,\Theta_2,\widehat{\Phi}_1,\widehat{\Phi}_2$ satisfy $E_4.V_1$ as defined above.

Now let's switch to $E_4.V_2$, where we need to prove the form of $\Theta_1,\Theta_2$. Again, mimicking $E_2.V_2$, we assume it will have the following form:
$$
\theta_1 + \theta_2 \widehat{u} + \widehat{\phi}_3 y + \widehat{\phi}_4 z = (\ldots)
$$

Where the RHS will contain public instance elements and commitments.

Let's for now expand $\theta_1 + \theta_2 \widehat{u} = w_2 (r_3 + s_3 \widehat{u}) = w_2 \widehat{c}_3$ (according to how we defined $\Theta_1,\Theta_2$). This is almost a pairing product, except $w_2$ is public (RHS would correspond to $e(W_2,\widehat{C}_3)$ which reveals $W_2$), so we will again expand it from the equation defining $D_2$:
$$
\begin{array}{c c l}
  \theta_1 + \theta_2 x
  & = & (d_2 - (r_2 y + s_2 z)) \widehat{c}_3 \\
  & = & d_2 \widehat{c}_3 - (r_2 y + s_2 z) \widehat{c}_3 \\
  & = & d_2 \widehat{c}_3 - (y (r_2 \widehat{c}_3) + z (s_2 \widehat{c}_3))
\end{array}
$$

This naturally defines $D_2 \widehat{C}_3$ as the RHS of $E_4.V_2$, and the following two proof elements:
$$
\begin{array}{c}
  \widehat{\phi}_3 = r_2 \widehat{c}_3 \\
  \widehat{\phi}_4 = s_2 \widehat{c}_3
\end{array}
$$

The verification equation is thus:
$$
\theta_1 + \theta_2 \widehat{u} + \widehat{\phi}_3 y + \widehat{\phi}_4 z = d_2 \widehat{c}_3 \tag{$E_4.V_2$}
$$

Switching now to $E_4.V_3$. There we need to prove the validity of $\widehat{\Phi}_1,\widehat{\Phi}_2$ in the following form:
$$
\widehat{\phi}_1 + \widehat{\phi}_2 x + \theta_3 \widehat{v} + \theta_4 \widehat{l} = (\ldots)
$$

Gladly, this is even easier than what we just done for $V_2$:
$$
\widehat{\phi}_1 + \widehat{\phi}_2 x = (\widehat{d}_3 - 1)(r_2 + s_2 x) = (\widehat{d}_3 - 1) c_2
$$

This means that $\theta_3 = \theta_4 = 0$, and
$$
\theta_3 \widehat{v} + \theta_4 \widehat{l} + \widehat{\phi}_1 + \widehat{\phi}_2 x  = c_2 (\widehat{d}_3 - 1)  \tag{$E4.V_3$}\\
$$

Finally, we need the last verification equation to "fix" the form of $\widehat{\Phi}_3,\widehat{\Phi}_4$ (and $\Theta_3,\Theta_4$), deriving which is also easy. Observe that $\widehat{\phi}_3 + \widehat{\phi}_4 x = (r_2 + s_2 x) \widehat{c}_3 = c_2 \widehat{c}_3$, therefore: 
$$ 
\theta_3 + \theta_4 \widehat{u} + \widehat{\phi}_3 + \widehat{\phi}_4 x  = c_2 \widehat{c}_3 \tag{$E4.V_4$}
$$ 
(The generic form that includes $\Theta_1,\Theta_2$ is here also because of $E_2.V_4$.)

As before, these equations are not yet "randomized" and thus not zero-knowledge. However, adding randomization is done exactly as before. First we add it to $\Theta_1,\Theta_2,\widehat{\Phi}_1,\widehat{\Phi}_2$ (so that the randomness cancels in $V_1$) and then propagate to the other set of proof elements. This does not change the form of verification equations, but only the proof elements.

The resulting set of proof elements for $E_4$ is:
$$
\begin{array}{ c l l l }
    \Theta_1 & = W_2^{r_3} g_3^\alpha g_4^\beta  \qquad & & \widehat{\Phi}_1 = (\widehat{D}_3/H)^{r_2} h_3^{-\alpha} h_4^{-\gamma} \\
    \Theta_2 &= W_2^{s_3} g_3^\gamma g_4^\delta  &&\widehat{\Phi}_2 = (\widehat{D}_3/H)^{s_2} h_3^{-\beta} h_4^{-\delta} \\
    \Theta_3 &= g_1^\alpha g_2^\beta &&\widehat{\Phi}_3 = \widehat{C}_3^{r_2} h_1^{-\alpha} h_2^{-\gamma} \\
    \Theta_4 &= g_1^\gamma g_2^\delta  &&\widehat{\Phi}_4 = \widehat{C}_3^{s_2} h_1^{-\beta} h_2^{-\delta}
\end{array}
$$
And the equations (in logarithms) are:
$$
\begin{array}{ c l r }
\theta_1 \widehat{u} + \theta_2 \widehat{l} + \widehat{\phi}_1 y + \widehat{\phi}_2 z & = d_2 (\widehat{d}_3 - 1) 
& \hspace{1cm} (E_4.V_1) \\
\theta_1 + \theta_2 \widehat{u} + \widehat{\phi}_3 y + \widehat{\phi}_4 z &= d_2 \widehat{c}_3 
& \hspace{1cm} (E_4.V_2) \\
\theta_3 \widehat{v} + \theta_4 \widehat{l} + \widehat{\phi}_1 + \widehat{\phi}_2 x  &= c_2 (\widehat{d}_3 - 1)  
& \hspace{1cm} (E_4.V_3) \\
\theta_3 + \theta_4 \widehat{u} + \widehat{\phi}_3 + \widehat{\phi}_4 x  &= c_2 \widehat{c}_3 
&  \hspace{1cm} (E_4.V_4)
\end{array}
$$
