#!/usr/bin/env bash
set -euo pipefail
exec 9>/workspace/recovery/operations/confirmation.lock
flock -n 9
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLCONFIGDIR=/workspace/recovery/mpl NUMBA_CACHE_DIR=/workspace/recovery/numba-cache
cd /workspace/recovery/restored/LANS-RISK/working/extended_baselines
printf 'START %s\n' "$(date -u +%FT%TZ)" >> /workspace/recovery/operations/events.log
set +e
/workspace/recovery/venv/bin/python experiment.py --stage confirmation --workers 4 >> /workspace/recovery/operations/confirmation.log 2>&1
result=$?
set -e
printf 'EXIT %s status=%s\n' "$(date -u +%FT%TZ)" "$result" >> /workspace/recovery/operations/events.log
exit "$result"
