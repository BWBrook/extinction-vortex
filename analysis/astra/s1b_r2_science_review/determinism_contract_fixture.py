"""Tiny temporary-fixture check of the published diagnostic's coverage contract.

No real population sampling and no production paths. Exercises only small
JSON journals, demonstrating why zero differences needs a coverage audit.
"""
import contextlib
from datetime import datetime
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'analysis/fable/calibration/v2_dev/p3_r2_determinism.py'


def main():
    spec=importlib.util.spec_from_file_location('diagnostic_under_review',SOURCE)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory(prefix='s1b-determinism-fixture-') as tmp:
        p=Path(tmp);a=p/'a';b=p/'b';dirs=p/'dirs.txt';out=p/'out.json'
        for r in (a,b):
            (r/'sets'/'s00001').mkdir(parents=True)
        line=json.dumps(dict(batch=0,proposal_in_batch=7,theta={'s':.5}))+'\n'
        for run,data in ((a,line+line),(b,line)):
            sd=run/'sets'/'s00001'
            (sd/'sh000000000.json').write_text(json.dumps(dict(first_batch=0,batches_done=1,
                                                             journal_bytes=len(data),journal_sha256='wrong')))
            (sd/'sh000000000_hits.jsonl').write_text(data)
        dirs.write_text('s00001\ns99999\n')
        with contextlib.redirect_stdout(io.StringIO()):
            mod.main(str(a),str(b),str(dirs),str(out))
        result=json.loads(out.read_text())
        assert result['total']==dict(settings=1,batches_compared=1,identical_lines=1,identity_only_equal=0,unmatched=0)
        receipt=dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
                     source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                     requested_settings=2,reported=result['total'],
                     fixture=dict(missing_requested_setting='s99999',earlier_duplicate_identity=True,
                                  deliberately_wrong_checkpoint_hash=True),
                     observation='The diagnostic reports zero differences while skipping a missing setting, collapsing a duplicate hit identity, and not checking journal hashes. This does not invalidate separately collected genuine smoke data.',
                     recommendation='Use verified journals and explicit requested/present/shared-batch coverage; sparse interval intersections avoid per-empty-batch memory and runtime.')
        (HERE/'determinism_contract_fixture.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
