# Adopted primary-null development candidate

Barry submitted this decision on **9 October 2026, 14:51:05 AEDT**
(`2026-10-09T03:51:05.102Z`). The
[verified submitted response](../docs/decisions/d36e602c-1c18-45fe-83ce-90adda12d313.md)
records option `approve_ar_cat_primary`:

> Approve ar_cat as the primary development candidate; retain iid as mandatory sensitivity (Astra and Fable recommendation).

No comment, alternative or deferral was submitted. The
[original proposal](vortex_null_proposal_20261009.md) and
[question definition](../docs/decisions/requests/vortex-primary-null-20261009.json)
preserve the context and scope of this choice.

## Adopted scope

- **Primary development candidate:** the no-feedback model with AR(1)
  environmental persistence and occasional external catastrophes (`ar_cat`).
  Its environmental transition law excludes abundance; this does not assert
  statistical independence between environment and abundance.
- **Mandatory labelled sensitivity:** iid Gaussian environmental noise.
- **Existing target:** reconstructed T1–T4 with the random-intercept primary
  estimator and random-slope sensitivity; T5/scaling descriptive, as in
  [Barry's earlier target amendment](vortex_target_amendment_20261009.md).
- **Next work:** develop and specify validation for the selected model. Fable
  retains ownership of the formal protocol and calibration implementation;
  Astra reviews the resulting design and measured cost inventory.

The fixed-K nearest-neighbour algorithm and larger banks remain development
proposals accepted for further work in the
[0.7 review](astra_protocol07_review_20261009.md). This response does not freeze
priors, beta_min, numeric corner scenarios, production settings, banks or
resource allocation. Fresh validation must assess the actual frozen procedure;
empirical p-values remain behind the existing validation gate.

The candidate and exploratory priors follow exposure to observed calibration
summaries and synthetic development results. Model selection does not validate
those priors or establish that catastrophes are necessary. Rejection would
concern this specified model; non-rejection would not establish absent feedback.
Historical reconstruction and the remaining source/census questions stay open.

## Verification and record

The connector collected and archived the form at `2026-10-09T03:55:15.285Z`.
A separate check verified the canonical JSON hash, equality to the original
definition, and all Markdown question/context/option/answer content. The
response hash is
`047051b91c4955b788decdb6d32131222e3366389f87e2b25df84bb656bffc86`.
The archived project listing includes the form and collection time; the active
listing is empty, with no further pages. Immutable response files were committed
first on the canonical Mac as `07c233e`, then fast-forwarded into WSL.
Correspondence 1255 relays the exact selected option and its scope.
