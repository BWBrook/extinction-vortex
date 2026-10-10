#!/usr/bin/env bash
set -euo pipefail
R=/data/fable/vortex/alt_check_20261010T081433Z; S=$R/src/analysis/fable/calibration
cd $R/src
python3 $S/time_generators.py $R/dev_scenarios.json $R/gen_times.json 20 13 20261030 > $R/gen_times.log 2>&1
python3 $S/build_bank.py $R/toybank 3000000 1 9 ar_cat 5 > $R/toybank.log 2>&1
echo '{"drift": {"form": "step", "hi": 2.0}}' > $R/sc_md.json
echo '{"detect": "lown"}' > $R/sc_mo.json
python3 -c "import json; c=[x for x in json.load(open('$R/dev_scenarios.json')) if x['name']=='ar_cat_low_s'][0]; json.dump({'fixed': c['fixed']}, open('$R/sc_corner.json','w'))"
python3 $S/e2e_benchmark.py $R/toybank ar_cat $R/smoke/mamd 2 20 50 4 31 0.9745192683713976 $R/sc_md.json > $R/smoke_mamd.log 2>&1
python3 $S/e2e_benchmark.py $R/toybank ar_cat $R/smoke/mo 2 20 50 4 32 0 $R/sc_mo.json > $R/smoke_mo.log 2>&1
python3 $S/e2e_benchmark.py $R/toybank ar_cat $R/smoke/corner 2 20 50 4 33 0 $R/sc_corner.json > $R/smoke_corner.log 2>&1
python3 $S/score_discrimination.py v2 $R/smoke 2 $R/smoke_scored.csv mamd mo corner > $R/smoke_summary.json
mkdir -p $R/smoke/nan && cp $R/smoke/mo/T_0.csv $R/smoke/mo/e2e_meta.json $R/smoke/nan/
python3 -c "import json; r=json.loads(open('$R/smoke/mo/e2e_rows.jsonl').readline()); r['p_hi']=float('nan'); open('$R/smoke/nan/e2e_rows.jsonl','w').write(json.dumps(r)+'\n')"
if python3 $S/score_discrimination.py v2 $R/smoke 1 $R/nan.csv nan > $R/nan.log 2>&1; then echo "NaN NOT CAUGHT"; exit 1; else echo "NaN caught: $(tail -1 $R/nan.log)"; fi
echo DONE
