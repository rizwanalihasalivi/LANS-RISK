# Verified LANS-Risk checkpoint snapshot —26100/44000

This is a recovery snapshot, not a completed confirmation result or a claim of controller superiority. The experiment remains stopped. All261completed batches and51frozen source/model files were verified both locally and inside the archive. See BACKUP_VERIFICATION.json, SNAPSHOT_MANIFEST.json and INVESTIGATION.md.

The archive contains code, configurations, models, checkpoints, logs, results, figures, manuscript files, earlier studies and prior backups. Git internals, regenerable caches and the virtual-environment symlink are excluded and listed in EXCLUSIONS.json. Package versions and environment records are preserved; the virtual environment itself must be recreated on a new host.

snapshot_parts contains48MiB chunks to stay below GitHub's per-file limit. Run `python restore_and_verify.py /path/to/output` to reassemble and verify the ZIP. Extraction is a separate explicit step. This command does not launch experiments.

Target repository:https://github.com/rizwanalihasalivi/LANS-RISK . Remote authentication/privacy/write access and remote storage must be independently verified before claiming a successful GitHub backup. Local commit creation is not proof of a remote backup. See RECOVERY_PLAN.md for safe resumption of the remaining17900episodes.
