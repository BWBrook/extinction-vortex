"""Repeat the reviewer cases, retaining separate parent receipts and source hash."""
import contextlib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'r2_node_review_20261025/combined_checks.py'
source = SOURCE.read_text()
needle = "(HERE / 'combined_checks.json')"
assert source.count(needle) == 1
code = source.replace(needle, 'Path(' + repr(str(HERE / 'parent_node_replay.json')) + ')')
with (HERE / 'parent_node_replay.log').open('w') as log, contextlib.redirect_stdout(log):
    exec(compile(code, str(SOURCE), 'exec'), {'__name__': '__main__', '__file__': str(SOURCE)})
result = json.loads((HERE / 'parent_node_replay.json').read_text())
result['replayed_source_sha256'] = hashlib.sha256(source.encode()).hexdigest()
(HERE / 'parent_node_replay.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'cases': list(result['cases']), 'node_sha256': result['node_sha256'],
                  'source_sha256': result['replayed_source_sha256']}))
