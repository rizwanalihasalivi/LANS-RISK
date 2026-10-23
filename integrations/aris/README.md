# ARIS integration for LANS-RISK

ARIS is installed locally as a pinned Codex skill pack, with its MIT license,
shared references, templates and helper tools. All 85 upstream Codex skills are
available through portable relative links in `.agents/skills`, alongside the
LANS-RISK-specific `lans-risk-resume` skill. No global installer or configuration
was changed. `UPSTREAM_LOCK.json` records the exact commit and every vendor hash.

From the repository root:

```sh
python integrations/aris/lans_risk.py verify
python integrations/aris/lans_risk.py status
python integrations/aris/lans_risk.py evidence
```

In a Codex session opened on this repository, invoke `$lans-risk-resume`.
The installed ARIS `experiment-audit`, `result-to-claim`, `analyze-results`,
`paper-plan` and `paper-writing` workflows can then use the preserved evidence.
Skill discovery may require opening a new session. This integration does not
claim that an ARIS model review has already run.

## Project mapping

| ARIS input | LANS-RISK evidence |
|---|---|
| Research status and missing experiments | `recovery_results/results/STUDY_COMPLETENESS.json` |
| Results and limitations | `recovery_results/results/SCIENTIFIC_REPORT.md` |
| Figures, tables, statistical methods | `recovery_results/results/` |
| Raw records and metadata | `recovery_results/working/` |
| Recovery and audit scripts | `recovery_results/operations/` |
| Frozen-protocol amendment proposal | `recovery_results/proposals/` |
| Immutable checkpoint hashes | `recovery_results/CHECKPOINT_MANIFEST.json` |
| Full original source/models | `snapshot_parts/`, restored by `restore_and_verify.py` |

The offline adapter verifies vendor integrity, every pre-integration tracked
file and all 1,742 checkpoint files. Its status is a saved scientific status,
not a live job monitor. The evidence helper only checks that cited values
occur in source files; it does not validate a claim's scientific interpretation.

## Execution boundaries

Main confirmation is complete (44,000 episodes), observation-delay is complete
(4,000), and runtime has 4,800 samples. Robustness is 231/264 conditions.
The remaining 33 dense-Merge conditions cannot run successfully under the
original initialization cap. The tested 200,000-attempt proposal remains
unapproved. ARIS installation is not approval to change the protocol.

Use the existing recovery environment and runners after any required explicit
scientific amendment approval. Do not rerun completed batches, silently alter
seeds or controllers, or let generic auto-fix/research loops change the freeze.

No model API, paid service, notification, scheduler, background process or cloud
rental is enabled by this integration. ARIS does not prevent host shutdowns or
supply compute. External review and complete-paper acceptance are NOT_RUN.
The existing verified available-results ZIP remains valid but does not contain
this later integration; distribute the companion integration archive alongside it.

## Updates and removal

The upstream snapshot is deliberately pinned. Do not run automatic upstream
updates during confirmation. To update later, separately review the new commit,
replace the vendor snapshot and regenerate its lock; re-run verification.
To remove this integration, remove `integrations/aris`, the added `.agents/skills`
links/custom skill, and this integration's AGENTS.md. No frozen source or saved
result needs modification. No global settings need undoing.
