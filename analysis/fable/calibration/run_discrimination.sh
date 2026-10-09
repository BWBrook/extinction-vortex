#!/usr/bin/env bash
# Development discrimination check (synthetic only): larger banks for iid and ar_cat,
# then e2e p-values for outer datasets generated under each null and under M_A
# (Delta10 = 0.5, beta = 8.66) on the same environment variant. Development replicate
# counts R = 1000 (production uses 2000). Usage: run_discrimination.sh RUNDIR N_OUTER
set -euo pipefail
RUN=$1; NOUT=$2
SRC=$RUN/src/analysis/fable/calibration
python3 $SRC/compare_nulls.py $RUN/banks2e8 200000000 1000000 18 iid,ar_cat 100 > $RUN/banks2e8.log 2>&1
status=0
for v in iid ar_cat; do
  python3 $SRC/e2e_benchmark.py $RUN/banks2e8 $v $RUN/disc_${v}_null $NOUT 1000 2000 1.0 14 0 20261016 > $RUN/disc_${v}_null.log 2>&1 & p1=$!
  python3 $SRC/e2e_benchmark.py $RUN/banks2e8 $v $RUN/disc_${v}_MA $NOUT 1000 2000 1.0 14 8.66 20261017 > $RUN/disc_${v}_MA.log 2>&1 & p2=$!
  wait $p1 || { echo "FAILED disc_${v}_null"; status=1; }
  wait $p2 || { echo "FAILED disc_${v}_MA"; status=1; }
done
for a in iid_null iid_MA ar_cat_null ar_cat_MA; do
  n=$(wc -l < $RUN/disc_$a/e2e_rows.jsonl 2>/dev/null || echo 0)
  [ "$n" -eq "$NOUT" ] || { echo "INCOMPLETE disc_$a: $n/$NOUT"; status=1; }
done
[ $status -eq 0 ] && echo DONE
exit $status
