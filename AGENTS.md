# LANS-RISK research integration

Read `integrations/aris/README.md` and use the project-local `lans-risk-resume`
skill for continuation. ARIS skills are installed in `.agents/skills`; their
pinned source and helpers are in `integrations/aris/upstream`.

User constraints take precedence over upstream AUTO_PROCEED, experiment fixes,
new ablations, reviewer suggestions, and paper acceptance defaults:

- Preserve frozen code, model tensors, seeds, settings, original 261 batches,
  and all subsequent verified results. Never overwrite historical evidence.
- All 440 main confirmation batches are done. Do not run them again.
- Dense-Merge robustness has 33 blocked conditions. Changing initialization
  attempts from 10,000 to 200,000 requires explicit user approval of that
  separate amended study. Installing ARIS does not grant that approval.
- No paid infrastructure or new charges. Do not launch external model APIs,
  cloud rentals, notification integrations, or an unattended paid review loop.
- No fabricated results, citations or significance. A deterministic checksum
  check is not independent scientific peer review. Label unperformed reviews.
- Use available local execution and existing recovery/audit scripts; do not
  substitute ARIS's generic training commands for the frozen study protocol.
- Never mark the entire study complete while any required condition is missing.

The repository root is a backup/recovery repository. Actual runnable frozen code
is restored separately. Consult `recovery_results/operations/START_HERE_ENVIRONMENT.md`.
Do not edit symlinked upstream skills. Add local adaptations separately.
