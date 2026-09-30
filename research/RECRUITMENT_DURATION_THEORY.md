# Duration composition as a selected-observation recruitment null

Task `recruitment-duration-null-001`, attempt 1, 2026-09-29. This is a prospective observation design, using standard probability bounds rather than a novel biological or mathematical theorem. It does not fit the retained Myo1E table or infer force. The question is whether different *marginal* fractions of Myo1E-positive observed tracks could arise solely from different duration distributions while one conditional positivity function is shared.

## Cohort, denominator, and restricted null

Let \(C\in\{0,1\}\) denote two correctly mapped acquisition conditions, \(S=1\) eligibility and retention under one declared tracking/selection rule, \(T\) the recorded **total observed track duration**, and \(Y\in\{0,1\}\) the declared Myo1E-positive classification. The denominator for \(p_c\) must contain *all eligible observed tracks*, positive and negative, counted under the same rule:

\[
 F_c=\mathcal L(T\mid C=c,S=1),\qquad
 p_c=\Pr(Y=1\mid C=c,S=1).
 \tag{1}
\]

This fraction is distinct from a positive-to-negative ratio \(R_c=p_c/(1-p_c)\). For the same validated exhaustive positive/negative cohort, \(p_c=R_c/(1+R_c)\); here the positivity rule, counts, and actual Figure 4C denominator still require verification, so no conversion is made from the retained table.

The selected-observation null is that one measurable function \(g:[0,\infty)\to[0,1]\) satisfies

\[
 \Pr(Y=1\mid T=t,C=c,S=1)=g(t)
 \quad(F_c\text{-almost everywhere, }c=0,1),\qquad
 p_c=\int g(t)\,dF_c(t). \tag{2}
\]

Thus \(Y\) and condition are conditionally independent given total observed duration **within the selected cohort**. Equal marginal positivity is not required when \(F_0\ne F_1\). Conversely, a marginal excess alone does not establish different conditional recruitment. Formula (2) is an observational restriction, not a causal exposure-time model.

## A simple population bound

Use the convention

\[
 d_{\rm TV}(F_0,F_1)
 :=\sup_A|F_1(A)-F_0(A)|
 =\frac12\int|dF_1-dF_0|. \tag{3}
\]

For every common \(0\le g\le1\), the layer-cake identity \(g(t)=\int_0^1\mathbf1\{g(t)>z\}\,dz\) gives

\[
 \boxed{\quad |p_1-p_0|\le d_{\rm TV}(F_0,F_1).\quad} \tag{4}
\]

The constant is sharp over all \(g\): a Hahn-set indicator attains the signed difference of the two measures. In particular, identical population duration distributions force equal marginal positive fractions under this null. Equation (4) is a necessary *population* restriction. It is not directly a significance test: for continuous durations, raw empirical measures from nonmatching finite samples can have TV equal to 1 even when their underlying populations overlap greatly. A prospective test needs a fixed duration representation or justified distribution estimator and uncertainty that respects movie/cell sampling.

## Sharp envelope when baseline positivity is fixed

Fix the exact population baseline fraction \(a=p_0\in[0,1]\). Write \(\mu=F_0\), \(\nu=F_1\), and take the Lebesgue decomposition

\[
 \nu=\ell\,\mu+\nu_s,\qquad s=\nu_s([0,\infty)),
 \tag{5}
\]

where \(\ell=d\nu_{\rm ac}/d\mu\ge0\) and \(\nu_s\) is singular to \(\mu\). Let \(\ell^\downarrow:[0,1]\to[0,\infty]\) be the decreasing rearrangement of \(\ell\) with respect to the probability measure \(\mu\), defined up to Lebesgue-null sets. It is integrable and \(\int_0^1\ell^\downarrow(v)dv=1-s\). The exact feasible interval for \(p_1\), ranging over all shared measurable \(g\in[0,1]\) with \(\int g\,d\mu=a\), is

\[
 \boxed{\quad
 L(a)=\int_{1-a}^{1}\ell^\downarrow(v)\,dv
 \ \le p_1\le\ 
 U(a)=s+\int_0^a\ell^\downarrow(v)\,dv.
 \quad} \tag{6}
\]

This is the standard threshold-allocation argument. To maximize \(p_1\), set \(g=1\) on the \(\mu\)-null support carrying \(\nu_s\), which spends none of the baseline budget \(a\), then allocate that budget to the largest values of \(\ell\). To minimize, set \(g=0\) on that singular support and allocate the budget to the smallest \(\ell\). Fractional values of \(g\) at a threshold give the exact budget when \(\mu\) has atoms or a positive-measure likelihood-ratio level set. Since \(g\) is a probability, fractional values are permitted; no nonatomic assumption is needed. Convex combinations of the maximizing and minimizing functions give every intermediate \(p_1\), so (6) is both necessary and sufficient for **two exact population marginals** under this unconstrained common-\(g\) null.

The endpoint cases show why support matters. If \(F_1\) is entirely singular to \(F_0\), then \(s=1\), \(L(a)=0\), and \(U(a)=1\) for any baseline \(a\); durations have no overlap to constrain the intervention marginal. If \(F_1=F_0\), then \(\ell=1,s=0\) and both bounds equal \(a\). Formula (6) also covers atoms and mixed continuous/discrete durations without treating zero baseline mass as zero intervention mass. It implies (4), while using the observed baseline fraction can make the feasible interval narrower.

For an **arbitrary illustrative** two-duration distribution, take \(F_0=(4/5,1/5)\), \(F_1=(3/10,7/10)\), and baseline \(a=2/5\). Here \(d_{\rm TV}=1/2\), so (4) alone allows \(p_1\) as high as \(9/10\). The fixed-baseline constraint \((4/5)g_1+(1/5)g_2=2/5\) instead gives \(3/20\le p_1\le31/40\). The lower endpoint uses \((g_1,g_2)=(1/2,0)\), and the upper uses \((1/4,1)\). A hypothetical \(p_1=17/20\) passes the simple TV bound but fails the sharp envelope. These fractions are not tuned to a study result and have no biological interpretation.

An equivalent computation, useful without rearrangements, uses \(m=\mu+\nu\), \(u=d\mu/dm\), and \(v=d\nu/dm\):

\[
 U(a)=\inf_{\lambda\in\mathbb R}\left\{\lambda a+\int(v-\lambda u)_+\,dm\right\},
 \qquad L(a)=1-U(1-a). \tag{7}
\]

The support where \(u=0,v>0\) contributes freely to the upper bound. At endpoint budgets the infimum may be approached as \(|\lambda|\to\infty\). The sharp envelope is a prospective falsification criterion: if a condition's true \(p_1\) lies outside it, no common measurable \(g\) can explain both selected marginals using only the two measured duration distributions. Failure to reject does not identify \(g\), prove a causal duration effect, or validate selection rules. With more than two conditions, separate pairwise envelopes need not ensure one \(g\) works jointly; use a joint feasibility problem.

## Finite bins and an implementable check

For a fixed, prespecified partition \(B_1,\ldots,B_K\) covering the eligible duration domain up to both \(F_c\)-null sets, let \(w_{ck}=F_c(B_k)\). A finite-bin null requires common within-bin positivity \(g_k\in[0,1]\), in the exact sense \(\Pr(Y=1\mid T\in B_k,C=c,S=1)=g_k\) whenever the conditional probability is defined. Then

\[
 p_c=\sum_{k=1}^{K} w_{ck}g_k,
 \qquad 0\le g_k\le1. \tag{8}
\]

For a fixed baseline \(a\), a small linear program minimizes or maximizes \(\sum_k w_{1k}g_k\) subject to \(\sum_k w_{0k}g_k=a\). Bins with \(w_{0k}=0,w_{1k}>0\) have the same free upper contribution as singular support in (6), and fractional \(g_k\) handles ties and bin masses. The binned TV bound \(|p_1-p_0|\le\tfrac12\sum_k|w_{1k}-w_{0k}|\) follows **under (8)**.

Common continuous \(g(t)\) alone does not imply common within-bin averages when the two conditions place different durations inside a bin. For a hypothetical single bin containing distinct values \(t_0,t_1\), take \(F_0=\delta_{t_0}\), \(F_1=\delta_{t_1}\), and \(g(t_0)=0,g(t_1)=1\). Both bin weights equal 1, but \(p_0=0,p_1=1\). Thus coarse-bin weights cannot silently replace the continuous population bound; the within-bin restriction must be defended, or duration resolution and regularity must be handled explicitly.

To test this design, one needs positive **and** negative eligible-track records, their total observed durations, verified condition and channel mappings, the Figure 4C denominator, movie/cell/culture group identifiers and baseline/post acquisition pairing, censoring and selection flags, and meaningful duration overlap. Freeze track eligibility, bins or estimator, and positivity rule before inspecting the condition contrast. Estimate uncertainty at independent sampling units, accounting for track clustering, mapping uncertainty and missing/censored tracks; evaluate an uncertainty region for \((p_0,p_1,F_0,F_1)\), not only a plug-in inequality from raw tracks. A marginal excess exceeding a noisy plug-in bound does not by itself prove a conditional difference.

The retained [Myo1E findings](MYO1E_FINDINGS.md) and [repository assessment](MYO1E_REPOSITORY_FINDINGS.md) do not yet establish those denominators, group/condition maps or positivity and lifetime definitions for the 1,709-row three-color table. Therefore no present-data test or Figure 4 reproduction follows. An authoritative codebook and eligible positive/negative cohort would be new prerequisites.

## Interpretation and relation to the earlier selection limit

Total observed duration is an endpoint, potentially altered by recruitment itself, by the intervention, and by tracking/censoring. Detection and retention may depend on duration, channel brightness, and recruitment. Conditioning on \(S=1\) or on total \(T\) can therefore create or hide condition associations through selection or collider paths. Equations (2)-(8) neither assert an independent exposure clock nor isolate a biological recruitment hazard. Rejecting the selected-observation null establishes a conditional observable difference under the declared measurement rules; it does not establish adaptive actin force, a single-event rescue mechanism, or direction of causation.

The earlier [DASC observation decision](DASC_OBSERVATION_DECISION.md) allows **arbitrary condition-specific selection** and shows why latent kinetics cannot then be identified from selected tracks. The common-\(g\) restriction here is deliberately narrower and falsifiable once its inputs are measured. It does not defeat the DASC impossibility for an unrestricted detector: selection can change \(F_c\), \(Y\), or the apparent \(g\), and the present records do not calibrate those paths. No browsing, download, data fit, solver call or numerical force calculation was performed for this note.
