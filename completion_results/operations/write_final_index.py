from pathlib import Path
import json
out=Path('/workspace/recovery/operations/final_verified_results')
assert json.loads((out/'FINAL_INDEPENDENT_VALIDATION.json').read_text())['status']=='PASS'
(out/'RESULTS_INDEX.md').write_text('''# Final results index

Start with [SCIENTIFIC_REPORT.html](SCIENTIFIC_REPORT.html) for the readable report and linked figures, or SCIENTIFIC_REPORT.md for editable text.

| Purpose | Files |
|---|---|
| Required stage coverage and amendment status | STUDY_COMPLETENESS.json; FINAL_COMPLETENESS_AUDIT.json |
| Independent numerical verification | FINAL_INDEPENDENT_VALIDATION.json |
| Definitions, uncertainty and tests | STATISTICAL_METHODS.md |
| Publication captions | FIGURE_CAPTIONS.md |
| Main confirmation | extended_baselines/fixed_fifo.pdf; publication_tables.pdf and .tex in that directory |
| All main baselines and ablations | extended_baselines/descriptive_metrics.csv and paired_tests.csv; ../project/deliverables/publication_results/confirmation/ contains inherited full ablation figures |
| Robustness | stress_study/weaker_actuation.pdf and denser_traffic.pdf; publication_tables.pdf/.tex; source_version labels identify amended dense Merge |
| Observation-delay distributions | observation_profiles.pdf; observation_delay_study/publication_tables.pdf/.tex |
| Runtime | runtime.pdf; runtime_current_host.csv; runtime_samples.json |
| Empirical delay thresholds | empirical_delay_tolerance.csv |
| Per-condition mean, SD, confidence intervals and observed extremes | descriptive_metrics.csv in each study directory |
| Paired contrasts, bootstrap effect intervals, raw and Holm-adjusted p values | paired_tests.csv in each study directory |
| Labelled episode records | episodes.jsonl in each study directory |
| Reproduction instructions | REPRODUCIBILITY.md |

Vector PDFs and high-resolution PNGs are supplied. Binary metrics in machine-readable descriptive tables are fractions; publication tables express them in percent. Actor-seed averages are descriptive, not extra independent traffic samples. Timing confidence intervals and metrics absent from original recordings are explicitly unavailable.

Original raw records, frozen models/configurations/code, historical checkpoints and studies are under ../project/. The approved amendment source, approval record, execution log and audits are under ../operations/. Dense-Merge raw records have their own amended_dense_merge_confirmation directory; the original robustness directory remains untouched. The current tracked GitHub repository and ARIS workflows are under ../aris_repository/.

Historical blocked reports are preserved under operations/verified_results and aris_repository/recovery_results/results. They describe earlier states. This results/ directory and aris_repository/completion_results/results govern final conclusions.
''')
print('Final file index written')
