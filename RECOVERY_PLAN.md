# Recovery plan — do not launch until authorized

1.Provision a non-preemptible persistent VM or dedicated host with at least4CPUcores, adequate RAM, persistent disk and an explicit no-idle-shutdown policy. Keep an independent remote copy. tmux/nohup alone cannot protect against VM/container termination.
2.Restore this snapshot and verify all archive/part hashes and all261completed batches before launching. Recreate the recorded Python environment:Python3.12.14,numpy2.3.5,numba0.68.0,torch2.14.1+cpu,stable-baselines3 2.9.0,scipy1.17.0; retain exact frozen source/model hashes.
3.Create a NEW preflight record for261completed batches. Do not run the older prepare.py blindly:it asserts236batches; the old supervisor also contains23600/20400-specific reporting. Those scripts are preserved as historical evidence, not the current recovery command.
4.Use only the original confirmation command, from working/extended_baselines:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
/path/to/verified/venv/bin/python experiment.py --stage confirmation --workers 4 \
  >> confirmation_recovery.log 2>&1
```

The original runner validates frozen sources and existing raw-result hashes, then returns cached results for all261valid batches. Only179missing batches/17900episodes require computation. Traffic seeds141000..141099 and all original settings remain unchanged. Interrupted incomplete batches have no mid-batch recovery and may rerun; completed batches must not rerun or be overwritten.
5.Use a systemd service or job scheduler to supervise this ONE confirmation command, with capped retries, persistent stdout/stderr, exit status and stop-reason logs. Do not chain robustness, observation-delay or other experiments. Check command identity/start time rather than stale PID files. Periodically sync completed .json/.jsonl pairs to durable storage; preserve manifests and never copy a metadata-only batch as complete.
6.At completion, verify440unique scenario/controller/policy-seed/delay condition keys,100specified traffic seeds per condition,44000unique composite episode keys, raw SHA256digests, unchanged frozen code/models, unchanged original261batches, and recomputed summary metrics. Then generate the verified confirmation report and stop for user review.

Current experiment settings and checkpoint writer are unchanged. If partial files appear after a future interruption, preserve/quarantine those incomplete pairs and investigate before resuming; never silently delete valid completed results.
