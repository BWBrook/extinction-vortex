#!/usr/bin/env bash
# Source snapshot is installed before this script runs in a named tmux session.
set -u
if [[ $# -ne 2 ]]; then
  echo "Usage: run_stage_b.sh SOURCE_ROOT NEW_ARTIFACT_DIR" >&2
  exit 2
fi
cd "$1" || exit 2
artifact_dir=$2
if [[ -e "$artifact_dir" ]]; then
  echo "Artifact directory exists; refusing overwrite" >&2
  exit 2
fi
mkdir -p "$artifact_dir" || exit 2
exec >"$artifact_dir/run.log" 2>&1
trap 'run_status=$?; printf "%s\n" "$run_status" > "$artifact_dir/exit_status.txt"; date -u +%FT%TZ > "$artifact_dir/finished_utc.txt"' EXIT
set -e
date -u +%FT%TZ > "$artifact_dir/started_utc.txt"
hostname > "$artifact_dir/hostname.txt"
cat SOURCE_COMMIT > "$artifact_dir/source_commit.txt"
find analysis/astra -type f -print0 | sort -z | xargs -0 sha256sum > "$artifact_dir/source_sha256.txt"
sha256sum data/raw/williams2021/population_data.csv > "$artifact_dir/input_sha256.txt"
Rscript analysis/astra/stage_b/test_gaussian_ml.R > "$artifact_dir/estimator_tests.txt" 2>&1
Rscript analysis/astra/m0/test_m0.R > "$artifact_dir/m0_tests.txt" 2>&1
Rscript analysis/astra/stage_b/run.R "$artifact_dir/reconstruction"
