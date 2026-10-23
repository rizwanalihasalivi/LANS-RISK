# ARIS review and revision record — LANS-RISK conference V4

The manuscript and framework were revised following an artifact-grounded ARIS research review and a fresh paper-to-evidence audit. The conference PDF is seven pages, with all 20 references cited, 12 controllers and all five measured command delays (0, 200, 500, 700 and 1,000 ms).

## Review assurance and scope

Two fresh native Codex reviewers were requested with `gpt-6-astra`, `ultra`, and no inherited conversation. The native tool returned agent identities but did not independently report the actual serving model or reasoning effort. Requested identities are therefore recorded separately from unknown actual identities. Both reviews are **same-family / provisional**. This is not journal/conference acceptance, human peer review, or an independently verified cross-family review.

- `/root/aris_full_review`: ARIS `research-review`, V3 initial review and V4 revision follow-up; source, all manuscript pages/figures, implementation, saved raw records and selected primary literature.
- `/root/aris_claim_audit`: ARIS `paper-claim-audit`, strict zero-context V3 manuscript/raw-evidence audit. It received no prior narrative or reviews. Its verdict is **WARN for scope limits**, with no material numerical discrepancy. It does not claim to audit the later V4 source. V4 uses identical result data/table cells; the full-paper reviewer inspected its revisions and independently checked the added Wilson example.

Original reports, input inventories and raw recomputations are in `review/`. Exact prompts and call traces are retained project-locally under `.aris/traces/`, following the ARIS tracing privacy instruction; they are not published in the ZIP. V3 audited manuscript/figure copies are retained there to make the version boundary explicit. Final V4 input hashes are in the revision review. No frozen experiment was changed, tuned, discarded or rerun.

**Final V4 reviewer verdict:** ready as a scoped empirical submission draft; all required local manuscript/diagram corrections resolved. This is a provisional assessment of the narrow claims. Remote artifact delivery is verified separately by the executor, not by the reviewer.

## Findings and revisions

| Finding | V4 action |
|---|---|
| Framework did not closely follow the requested layout | Recreated wide black/white serif control diagram: prediction at top, PPO in middle, memory branch below, tall supervisor at right, FIFO/plant/observation feedback at bottom. Vector PDF/SVG and high-resolution PNG included. |
| General information-matching wording included PPO incorrectly | Restricted the matching claim to nominal LANS–MPC. Documented the actor's legacy 18-D features, missing full NPC/FIFO information and direct-action deployment. |
| Benchmark/actor reproducibility detail was sparse | Added actual NPC counts, speed references/proposal ranges, goals and nonterminal completion. Added `METHODS_SUPPLEMENT.md`, exact source excerpts and checkpoint-recorded metadata for all 12 actors. |
| No-trajectory limitation mentioned only RMSE | Extended it to collision/corridor events, command histories and unpersisted transient diagnostics. |
| Retention and ranking benefits were not separately isolated | Explicitly states missing nominal mechanism-specific ablations and avoids attributing gains to them. |
| Earlier LANS metric distinction was too broad | Clarified that earlier work includes conventional and failure-penalized metrics; current article reports unpenalized episode RMSE. |
| Inference was difficult to inspect from headline values | Added actor-specific Merge Wilson interval example and identified the exact CSV/supplement locations. |
| Initialization proposals could be mistaken for accepted uniform samples | Described speeds as proposed uniform draws and explained rejection-conditioned scene distributions. |

The framework preserves the requested visual composition while showing the implemented LANS-RISK blocks. The reference image's EKF, latency-gain path and LQR–PPO actuation fusion are not present in the executed LANS-RISK controller and are therefore not depicted as implemented modules. LQR advice is an inherited policy input feature, disclosed in the methods supplement.

## Independently recomputed results

Reviewers reconciled all 44,000 original episode records in 440 batches, all 60 aggregate and 240 scenario table cells, all 3,440 paired tests and study-wide Holm adjustments, and all empirical delay endpoints. The claim audit also checked available descriptive means, sample standard deviations, extremes/quantiles and Wilson endpoints. No numerical inflation, best-seed substitution or pairing error was found.

| LANS-RISK comparison | Positive / equal / negative corridor-rate contrasts | Holm-significant positive contrasts |
|---|---:|---:|
| Nominal MPC | 9 / 51 / 0 | 0 |
| No prediction | 45 / 15 / 0 | 45 |
| No actor | 0 / 60 / 0 | 0 |
| PPO only | 49 / 11 / 0 | 45 |

These are correlated actor/scenario/delay contrasts, not 60 independent replications. LANS and nominal MPC share observed contiguous passing thresholds: Highway and Intersection 1,000 ms, Merge 700 ms and Roundabout 500 ms. Matching thresholds and nonsignificance do not establish equivalence. The actor has no observed corridor-rate benefit on this finite grid. Tracking differences are scenario dependent.

## Remaining scientific limits

The contribution remains an empirical integration/characterization study, with uncertain fit for venues requiring major algorithmic novelty. No isolated nominal retention/ranking ablation, information-matched delay-trained RL comparator, or reproduced external SOTA experiment is supplied. These are limitations for stronger future claims, not experiments silently added to this frozen revision.

The benchmark is synthetic; collision/corridor tests are sampled, and neither certified safety nor a real-time deadline guarantee is established. Episode-level logs support recomputation of summaries/tests but not independent reconstruction of complete trajectories. The review did not regenerate every saved bootstrap interval, establish every checkpoint's full training history, or independently prove the historical no-tuning chronology.

Five supplied literature works received primary-source contextual checking. Exhaustive latest-version/publisher metadata verification remains incomplete: live Crossref/PMLR/OpenReview requests were blocked by the network proxy. Existing source-access levels remain documented in `LITERATURE_REVIEW_NOTES.md`. No claim of exhaustive SOTA coverage or citation-audit completion is made.

## Future work boundaries

No new experiment is needed to report the present narrow findings honestly. Broader claims would require separately planned retention/ranking ablations, an information-matched delay-trained policy and/or reproduced external algorithms. Their compute cost cannot be reliably estimated without a new protocol. They were not run and are not represented as completed. Author/venue checks and any actual submission decision remain separate from this provisional model review.
