---
name: lans-risk-resume
description: Resume LANS-RISK from preserved evidence using the installed ARIS workflows, respecting its frozen scientific protocol and recorded blockers.
---

1. Read repository AGENTS.md and integrations/aris/README.md.
2. Run `python integrations/aris/lans_risk.py verify`. Stop dependent work if any
   protected or checkpoint hash fails. Preserve evidence; diagnose differences.
3. Run `python integrations/aris/lans_risk.py status` and read
   recovery_results/results/SCIENTIFIC_REPORT.md and STUDY_COMPLETENESS.json.
4. Run `python integrations/aris/lans_risk.py evidence` for the factual count
   evidence precheck. This proves cited values exist, not scientific validity.
5. Continue from existing operations checkpoints. Skip completed conditions.
   The dense-Merge amendment requires explicit approval; inspect the proposal
   and preflight under recovery_results/proposals before any authorized run.
6. For a requested ARIS review, read the relevant installed experiment-audit,
   result-to-claim or paper-writing skill and its referenced contracts first.
   Resolve helper paths under integrations/aris/upstream/tools. Respect user
   cost restrictions. If a reviewer is unavailable, record NOT_RUN or
   REVIEW_UNAVAILABLE; never manufacture acceptance or reviewer identities.
7. Save new integration/review artifacts separately. Re-run existing scientific
   audits after any authorized experiment. Produce a new ZIP and manifest;
   preserve the previous ZIP. Report original versus amended protocols clearly.
