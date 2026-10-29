#!/bin/bash
# Build the Stage 1b round-3 stage from a commit (design 9h): the files as committed, a checksum list, and a tar with
# sorted names, fixed owners and the commit's time, so the same commit always yields the same tar. Usage, from the
# repository root: build_stage_r3.sh COMMIT OUT_TAR
set -euo pipefail
REV=$1; OUT=$2; G=$(mktemp -d); C=analysis/fable/calibration
mkdir -p $G/src/$C/v2_dev $G/src/$C/kunanyi $G/s1b
for f in v2_dev/p1_sampler.py v2_dev/p2_stage1a.py v2_dev/p3_stage1b.py v2_dev/p3_r2_determinism.py kunanyi/s1b_node.pbs \
         kunanyi/s1b_collect.pbs kunanyi/s1b_submit.sh kunanyi/s1b_capacity.sh kunanyi/s1b_round3_dispatch.sh \
         kunanyi/s1b_topup_dispatch.sh; do
  git show "$REV:$C/$f" > "$G/src/$C/$f"
done
(cd $G && find . -type f ! -name stage_sha256.txt | sort | xargs sha256sum > s1b/stage_sha256.txt)
T=$(git log -1 --format=%ct "$REV")
tar --sort=name --mtime=@$T --owner=0 --group=0 --numeric-owner --mode=u+rw,go+r --format=gnu -cf "$OUT" -C $G .
rm -rf $G
sha256sum "$OUT"
