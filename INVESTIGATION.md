# Interrupted confirmation: evidence and limits

## Confirmed evidence

-261completed batches,26100episodes;17900episodes remain. Archived raw hashes, counts, traffic seeds and all51frozen source/model files verified.
-Last valid batch:intersection_lans_seed44_delay200.json, saved2026-10-22 09:40:38.121145UTC (17:40:38Asia/Shanghai).
-No experiment.py/run_study.py/resume_confirmation.py simulation processes are currently active. Old numerical PIDs can be reused by unrelated inspection commands; command identity must be checked.
-The resume log ends after a successful batch. No EXIT marker and no ERROR.log/traceback were saved. STATUS.json saying running is stale.
-The current PID1 began approximately2026-10-22 09:42:08UTC (17:42:08Asia/Shanghai), after the last saved batch. The prior run began09:21:06UTC. This supports replacement/reset of the process environment rather than an orderly experiment exit.
-Current cgroup memory.events reports oom=0 and oom_kill=0. These counters apply to the current environment; they do not establish what happened to the old one.
-Kernel dmesg access is denied; journalctl reports no journal files. No platform termination event or exit signal is available here.
-Previous interruption occurred at23600episodes; the subsequent run advanced to26100. There is no evidence of a deterministic failure at the same episode boundary.

## Possible causes, not established

Environment/session lifecycle teardown or replacement is consistent with the observed PID1 start and simultaneous loss of parent/workers. Idle limits, platform maintenance, explicit reset, host eviction, SIGKILL or prior-environment OOM are possible triggers, but none is confirmed. High CPU utilization alone is not evidence of a crash. A controller exception is not documented in the available logs.

## Remote access investigation before publishing

Configured destination:https://github.com/rizwanalihasalivi/LANS-RISK . gh auth status reports the configured GH_TOKEN invalid; GraphQL and REST repository metadata queries return Forbidden. These failures may involve credential validity or access-layer restrictions; they do not prove the repository is absent. The metadata API does not establish repository privacy or authenticated account identity. Separately, Git accepted a non-mutating push dry run to the exact user-authorized destination and a new backup branch, establishing an available Git write route. The repository is identified as private by the user; privacy cannot be independently confirmed via the blocked API. Actual remote storage will be verified by push, remote-ref comparison, and an independent fetch/restore. No remote-backup success is claimed by this pre-upload snapshot itself.
