# Completed Python robustness continuation — 3 November 2026

**All 264 robustness conditions / 13,200 episode records are verified under the disclosed initialization amendment.** Original 231 frozen conditions are unchanged; 33 dense-Merge conditions use the recorded approved 200,000-attempt sampler. Four were already saved; this task computed only the remaining 29 / 1,450 episodes. The original unamended stage alone remains 231/264.

Main confirmation (44,000), exploratory observation delay (4,000) and development (4,800) remain complete and re-audited. Across those stages and completed robustness there are 66,000 saved episode records, not 66,000 independent traffic samples. The prior 4,800 runtime calls were not remeasured in this continuation.

The dense-Merge LANS actors have zero observed collisions and 100% task completion at 0/500/1000 ms command delay on the fixed 50 traffic seeds per actor. Corridor completion is 100%/96%/40%, respectively: at 1000 ms the corridor criterion fails. Matched nominal MPC also has zero collisions and identical completion/corridor endpoints, with lower mean RMSE in these dense-Merge cells. These results do not establish universal superiority, statistical equivalence, certified risk or real-vehicle safety.

`audits/` retains source/raw/coverage checks and original-result hash preservation. `analysis/stress_study/` contains condition/seed-specific descriptive statistics, Wilson intervals, paired bootstrap contrasts, exact binary/Wilcoxon tests with Holm adjustment, enriched episode records, and figures. Source-version labels preserve original versus amended conditions. Missing diagnostics are not fabricated.

This is the historical LANS-RISK synthetic-traffic benchmark, separate from the new integrated bicycle pipeline. No Webots run or independent scientific peer review is claimed. Existing recovery_results and completion_results were not replaced.

To restore the saved completion pairs after recreating the original runtime, run `python python_campaign_20261103/restore_results.py --target /workspace/recovery/restored/LANS-RISK`. It verifies this checkpoint manifest, refuses differing existing files, and never launches an experiment. The setup installer alone restores the older checkpoint; this explicit completion restore is also needed.
