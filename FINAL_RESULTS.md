# Final verified experimental results

The required LANS-RISK plan is complete under the explicitly approved dense-Merge initialization amendment. Read [the final scientific report](completion_results/results/SCIENTIFIC_REPORT.md), [the file index](completion_results/results/RESULTS_INDEX.md), and [the independent validation](completion_results/results/FINAL_INDEPENDENT_VALIDATION.json).

- Main confirmation: 440 conditions / 44,000 episodes; all original 261 batches preserved.
- Robustness: 264 conditions / 13,200 episodes, comprising 231 original conditions and 33 separately labelled dense-Merge conditions using the approved 200,000-attempt initialization limit.
- Observation-delay: 200 conditions / 4,000 episodes.
- Runtime: 96 conditions / 4,800 warmed samples.
- Development: 240 conditions / 4,800 episodes, separately re-audited.

Independent numerical validation recomputed 7,776 metric rows and 6,224 paired tests and Holm adjustments, including supported bootstrap confidence intervals. Main LANS and nominal MPC have tied observed contiguous passing delay thresholds. Dense-Merge completion/safety rates tie, while nominal MPC has lower mean RMSE at all three evaluated delays. The report retains losses and statistical limitations; no universal LANS advantage, formal safety guarantee, or external-model peer review is claimed.

The repository root README and recovery_results preserve the earlier backup and blocked state as history. completion_results/results is the current authoritative report. Original models, sources, seeds, settings and results remain preserved; the amendment has its own source fingerprint, raw-result directory and explicit approval record. The ARIS adapter now reads this final state.

The complete downloadable ZIP is delivered through the chat workspace as LANS_RISK_FINAL_VERIFIED_RESULTS.zip, with its SHA256 sidecar. GitHub preserves the data, reports, source and recovery provenance on integration/aris-frozen-workflow.
