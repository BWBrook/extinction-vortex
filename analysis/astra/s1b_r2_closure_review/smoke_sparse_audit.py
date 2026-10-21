"""Read-only independent round-two smoke comparison, run on deep-server via stdin.

Checks committed journal lengths, hashes, order and unique identities, then
intersects batch intervals without materializing empty proposal batches.
No simulator, runner imports, library assembly or production mutation.
"""
from bisect import bisect_right
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

A=Path('/data/fable/vortex/v2_dev/p3/smoke_deep3')
B=Path('/data/fable/vortex/r2dev5/s1b/smoke_r2')
DIRS=('s00073','s00142','s00247','s00772','s01080','c00021')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def committed(run,d):
    folder=run/'sets'/d
    assert folder.is_dir()
    ranges=[];records={};hashes={}
    for path in sorted(folder.glob('sh*.json')):
        s=json.loads(path.read_text());a=s.get('first_batch',int(path.stem[2:]));end=a+s['batches_done']
        hashes[str(path.relative_to(run))]=sha(path)
        if end>a:
            ranges.append((a,end))
        journal=path.with_name(path.stem+'_hits.jsonl')
        size=s['journal_bytes']; raw=journal.read_bytes() if journal.exists() else b''
        assert len(raw)>=size
        if s['status'] in ('complete','failed','cancelled'):
            assert len(raw)==size
        data=raw[:size]
        assert hashlib.sha256(data).hexdigest()==s['journal_sha256']
        assert data.count(b'\n')==s['hits']
        hashes[str(journal.relative_to(run))]=hashlib.sha256(data).hexdigest()
        previous=(-1,-1)
        for line in data.splitlines(True):
            r=json.loads(line);key=(r['batch'],r['proposal_in_batch'])
            assert a<=key[0]<end and 0<=key[1]<20000
            assert key>previous and key not in records
            previous=key;records[key]=line
    ranges.sort()
    assert all(ranges[i][1]<=ranges[i+1][0] for i in range(len(ranges)-1))
    return ranges,records,hashes


def intersection(a,b):
    i=j=0;out=[]
    while i<len(a) and j<len(b):
        lo=max(a[i][0],b[j][0]);hi=min(a[i][1],b[j][1])
        if lo<hi:
            out.append((lo,hi))
        if a[i][1]<b[j][1]:
            i+=1
        else:
            j+=1
    return out


def main():
    expect=json.loads((B/'determinism_vs_deep3.json').read_text())
    per={}; hashes={};total=dict(settings=0,batches_compared=0,records_compared=0,identical=0,bytes_differ=0,unmatched=0)
    for d in DIRS:
        ra,ha,sha_a=committed(A,d);rb,hb,sha_b=committed(B,d)
        hashes[d]={'earlier':sha_a,'later':sha_b}
        overlap=intersection(ra,rb);starts=[r[0] for r in overlap]
        def inside(k):
            ix=bisect_right(starts,k[0])-1
            return ix>=0 and k[0]<overlap[ix][1]
        keys_a={k for k in ha if inside(k)};keys_b={k for k in hb if inside(k)}
        common=keys_a&keys_b
        st=dict(batches_compared=sum(hi-lo for lo,hi in overlap),
                records_compared=len(keys_a|keys_b),
                identical=sum(ha[k]==hb[k] for k in common),
                bytes_differ=sum(ha[k]!=hb[k] for k in common),
                unmatched=len(keys_a^keys_b))
        assert st==expect['settings'][d],(d,st,expect['settings'][d])
        per[d]=st|dict(earlier_shard_ranges=len(ra),later_shard_ranges=len(rb),overlap_intervals=len(overlap),
                       positive_nonpilot_coverage=bool(overlap),
                       earlier_total_committed_batches=sum(y-x for x,y in ra),
                       later_total_committed_batches=sum(y-x for x,y in rb))
        total['settings']+=1
        for k in st:
            total[k]+=st[k]
    assert total==expect['total']
    ca=json.loads((A/'collect_W1.json').read_text());cb=json.loads((B/'collect_W1.json').read_text())
    libmatches=[]
    for r in cb['rows']:
        if r['status']=='COMPLETE':
            d=r['dir']; pa=A/'lib'/f'{d}.jsonl';pb=B/'lib'/f'{d}.jsonl'
            assert sha(pa)==sha(pb)==r['library_sha256']
            assert pb.read_bytes().count(b'\n')==2000
            libmatches.append(dict(dir=d,sha256=sha(pb),shared_pilot_only=d=='s00772'))
    out=dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),runs=[str(A),str(B)],
             scope='Six named W1 smoke settings; no production round-two or n300 replay comparison. All shard journals verified before sparse comparison.',
             totals=total,positive_nonpilot_settings=sum(v['positive_nonpilot_coverage'] for v in per.values()),
             settings=per,library_matches=libmatches,
             old_collection_sha256=sha(A/'collect_W1.json'),new_collection_sha256=sha(B/'collect_W1.json'),
             published_determinism_sha256=sha(B/'determinism_vs_deep3.json'),journal_receipts=hashes,
             findings='All compared records match. The fourth identical library s00772 is imported pilot only. Intersections establish equality where both runs committed; they do not establish replay coverage of every requested batch.')
    print(json.dumps(out,indent=2,allow_nan=False))


if __name__=='__main__':
    main()
