# Completed descriptive artifacts and next bounded work

Astra, 14 October 2026. Review of Fable's handoffs 1621 and 1623 at
`ec72dd0330b6acd440aa85d2507c28e465ed2020`. This integrates three bounded
reviews and the existing caribou source audit. The peer's drafts and source
values were not edited. No new population simulation, reference sampling,
model fitting, bank loading or empirical test was performed.

**Disposition:** accept the Haley package and core draft for continued
manuscript production, with the finite corrections below. Accept the
descriptive caribou case and nine-series table proposed in 1623, within
Barry's narrowed deep-dive direction. The external-information revision now
supports an optional, bounded Stage 0 assignment after its execution checks;
this is development only and must not delay the paper. Stage 1 is not
commissioned. No general protocol rewrite is needed for these assignments.

## 1. Haley and the core manuscript

The [Haley artifact review](astra_haley_artifact_review_20261014.md) verifies
the source transcription, both CSV tables and the figure rebuild. The source
values and discrepancies are retained. Finish the figure/caption and narrative
repairs: scope seasonal maxima to the Bryant years; flag both sides of the
1988-to-1989 conflict; distinguish tagged cohorts and later sightings from
documented deaths; and describe recorded immigration without claiming that
the population's persistence depended on it. Agreement after exposure to the
earlier transcription is a separate extraction, not a blinded replication.
The conflict register should preserve possible explanations, including source
error, rather than declare why conflicting totals differ.

The [core manuscript review](astra_core_manuscript_review_20261014.md)
reconciles all 17 v1 validation totals and the effect and bank receipts. It
gives concrete corrections to notation, failure accounting and chronology.
Two apparently conflicting quantities must be preserved: **0.10** is the
minimum absolute ten-year risk increase in the design rule; **Delta10=0.075**
is the first tested feedback-grid point crossing it. The recorded increase
there is 0.13581. The reverse-time log-growth equation has the correct sign;
define its indexing and T4's refit rather than change the analysis.

Narrow the abstract's general necessity claim to the failure of this specified
procedure. Additional demographic evidence is a motivated direction, not
proven necessary or sufficient by these experiments. Preserve the distinction
between A's paired results and B's post-hoc calibration-table rescore. Matching
likelihoods at common covariance parameters is not identical optimized fits;
matching rounded neighbour distances is not proof of historical membership
at ties. Fresh v1 validation followed a freeze after progressive exposure to
reconstruction and development results. These limits belong in the paper.

## 2. Caribou and the nine-series table: accept the finite tranche

Message 1623 relays Barry's words from his Claude chat on 14 October:
"Yes, agreed, I think the second caribou case study would round it off nicely,
without bloat. Propose caribou and the nine-series table to Codex."
Fable offered to implement; Astra accepts the review role. The six proposed
caribou deliverables and one-page nine-series table are a suitable scope.

Use the [existing source audit](astra_caribou_recovery_review_20261014.md)
and corrected recovery matrix. Make these small changes during production:

- Call composition **calves per classified non-calf**, unless a particular
  source actually supplies a cow denominator. The preprocessing denominator
  is not automatically cows. Published collar totals are not annual KM risk
  sets; retain processed uncertainty provenance and distinguish IPM outputs
  that reuse the count data.
- Pin the Git file hashes actually used. Claim equivalence to an individual
  Zenodo ZIP only where its relevant file hashes were checked. Two distinct
  ZIP checksums do not by themselves establish equivalence of every input;
  another large download is unnecessary for this descriptive tranche.
- Preserve Maligne's group IDs, locations and flight dates. IDs 423/424 are
  not exact duplicates; ID 378 has blank total/composition, not an absent
  record. Keep the 2010 quantified subtotal and unresolved record distinct.
- Keep Purcells OTC, MNKA and MC separate, including the 2005 zero sighting
  with track evidence and the 2006 official zero. Neither dates the last
  animal's death. Retain the geographic naming/boundary caution around the
  2012 augmentation: its South label does not alone reconcile all historical
  Central/South definitions.
- Keep Banff's archived 2008 zero beside the documented April 2009 avalanche.
  The avalanche is a known proximate event; its documentation does not identify
  demographic feedback or resolve the archive's year convention. Do not call
  the endpoint mechanism wholly unknown.
- Use a record-specific conclusion: **these recovered records do not identify
  abundance feedback without additional observation and causal assumptions**.
  The source review is not an impossibility theorem about all count data.

For the nine-series table, replace "Independent demographic evidence" with
**"Demographic evidence and relationship to counts"**. Distinguish individual
histories, same-survey composition, count-derived summaries and transferred
rates. Shared monitoring is not automatically circular; reuse of the same
count likelihood matters. Label full-text, abstract-only and unverified leads
where relevant. Separate source-value matching from historical estimator
reproduction, and deposited windows from the analysed windows. Unknown
management or movement remains unknown, not zero. A compact readable page
with codes/footnotes may point to the existing detailed audits; a machine-
readable backing table can preserve the source detail without enlarging the
manuscript narrative.

Stop after the six caribou deliverables and nine-series table are complete,
source-linked and visually checked. Haley remains the main case; the three
caribou herds form one contrasting case outside the F&H nine. No broad new
search, Palmer/checkerspot work, author contact, fitted reconstruction, new
interval or empirical feedback test is included.

## 3. External information: bounded Stage 0, with execution corrections

Revision 2 resolves the main law, likelihood and fixed-K objections. The
joint prior/path draw followed by selection supports likelihood weighting
without inverse-selection weights. Explicitly distinguish the fixed-parameter
low-s corner from the prior-predictive blocks; not every outer draws theta
from prior (b). Specify that k and r are conditionally independent given theta
and that n is a per-population ideal information index. Replace "realistic E"
with "noisy stylized E" throughout.

The [deterministic checks](../analysis/astra/artifact_review_20261014/info_checks.json)
verify the formulas and useful implementation fixtures. Forty-node Gaussian
quadrature agrees with adaptive integration within 7.8e-16 over 45 checked
cases. The sampled and ideal log-likelihood expressions agree with separate
calculations. Stable log-weight normalization handles underflow; unusable
weights must be reported, never silently replaced by uniform weights.

Fable may implement and execute this optional **no-fit Stage 0** within the
standing development/resource scope, after binding the following routine
checks in its inputs file:

1. Use original v1 selected-row theta, with six parameter fields, source-row
   hashes and IDs. A-power's compact outer records are not a theta source.
   Verify all 800 original outer datasets before computation.
2. Bind frozen population order, scenario order b1/b3/b5/b16, n=30/300 cell
   map, stream tuples, k-then-r draw order, helper hashes, NumPy/SciPy and
   BitGenerator. The 16,000 proposed initial states are distinct in the
   reviewed runtime; this is not proof of collision-free/nonoverlapping streams.
3. Use k=K=2,000 with the fixed mask/MAD and bank/shard order; record actual
   member draw IDs. Equal rounded K-th distances do not resolve ties. Pin the
   query runtime and retain any mismatch instead of asserting exact historical
   membership without evidence.
4. Declare the quadrature and stable log-weight/nonfinite rules, with tiny
   fixtures for boundaries, uniform weights, concentrated weights and invalid
   inputs. Reuse neighbour rate functionals across n and the ideal comparator.
5. Follow the standing host/resource checks. Measure time and peak memory
   during a bounded setup pass before the full diagnostic; retain a one-pass,
   per-population plan with no bank expansion. Thirty minutes is an unmeasured
   estimate. Report a material resource shortfall rather than silently expand.

The fixed scope is eight cells, 200 exposed outers per cell and nine
populations, with both noisy and ideal weights. This is 800 distinct outer
datasets and 7,200 neighbourhoods; 28.8 million member weights of each type.
No new outer draws, reference sampling, fits, empirical calculations or larger
bank are needed. Return the support/cost report and stop.

Treat **ESS<100 as a declared exploratory concentration flag**, not an
established calibration threshold or frozen fitted failure rule. Report
continuous ESS and maximum weight share, unchanged C radii, unusable weights,
and any-of-nine flag fractions separately by scenario, n and noisy/ideal
comparator. Preserve all fixed denominators; a Stage 0 flag rate is not a null
non-accept or detection rate. Stage 0 cannot measure calibration or power.
Those would require a separately accepted fitted stage; its 40-minute Kunanyi
estimate is also unmeasured. Dependent evidence, bias, other corners, timing
and oracle-6 remain deferred. No validation or empirical permission follows.

## Evidence and next response

Receipts and reproduction scripts are in
[`analysis/astra/artifact_review_20261014/`](../analysis/astra/artifact_review_20261014/).
These extend existing audits; they do not repeat all raw-result or literature
checks. Fable is next: repair the descriptive/manuscript wording and produce
the accepted caribou/table package. Stage 0 is optional and stops at its own
report. Astra reviews the returned artifacts. No Barry decision is needed
for the routine repairs above.

14 October 2026, 15:10:54 AEDT (Australia/Hobart).
